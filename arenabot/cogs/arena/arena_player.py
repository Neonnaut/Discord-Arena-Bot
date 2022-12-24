
#
from typing import Type
import validators
import random

class Player:
    def __init__(self, stats):

        self.userID = int(stats[0])
        self.username = (stats[1][:17].strip() + '...') if len(stats[1]) > 20 else stats[1]
        self.combatant = (stats[2][:17].strip() + '...') if len(stats[2]) > 20 else stats[2]

        self.AT = int(stats[3]) * 20
        self.IN = int(stats[4]) * 10
        self.DF = int(stats[5]) * 10
        self.AR = int(stats[6]) * 20
        self.HP = int(stats[7]) * 80 + (int(stats[9]) * 10)
        self.SP = int(stats[8]) * 5
        self.EN = int(stats[9]) * 10
        self.wins = int(stats[10])
        
        self.abilities = [stats[11], stats[12]]

        try:
            if not validators.url(stats[14]):
                self.image = "https://cdn.discordapp.com/attachments/1001705046213398530/1036511658773839902/unknown.png"
            else:
                self.image = stats[14]
        except:
            self.image = "https://cdn.discordapp.com/attachments/1001705046213398530/1036511658773839902/unknown.png"

        self.effects = []

        self.weapon = stats[13]

        # Setup passive abilities
        if "dodge" in self.abilities:
            self.dodge = True
            self.effects.append("dodge")
            self.abilities.remove("dodge")
        else:
            self.dodge = False
        if "mount" in self.abilities:
            self.effects.append("has_mount")
            self.abilities.remove("mount")
            self.AT += 20
            self.DF += 10
            self.SP += 5

        if "resist" in self.abilities:
            self.effects.append("resist")
            self.abilities.remove("resist")

        if "guard" in self.abilities:
            self.effects.append("guard")
            self.abilities.remove("guard")

        self.temp_focus = False
        self.perm_focus = False

        self.knife = False
        self.set_weapon()

    def get_player_id(self):
        return self.userID

    def set_damage_to_hp(self, new_hp):
        self.HP = self.HP - new_hp

    def set_healing_to_hp(self, new_hp):
        self.HP = self.HP + new_hp

    def get_en_cost(self, en_cost = 5):
        if self.EN < en_cost:
            return f"This action requires {en_cost} endurance."
        return None

    def set_damage_to_en(self, en_cost = 5):
        self.EN = self.EN - en_cost

    def set_weapon(self):
        match self.weapon:
            case 'knife'|'dagger':
                self.knife = True
            case 'sword'|'scythe':
                self.AT += 40
            case 'spear'|'pike':
                self.SP += 10
            case 'greatsword':
                self.AT += 20
                self.DF += 10
            case 'mace'|'axe'|'hammer'|'staff':
                self.SP += 5
                self.DF += 10
            case 'bow'|'carbine'|'special'|'wand'|'sceptre':
                self.IN += 20
            case 'crossbow'|'shotgun':
                self.IN += 10
                self.AT += 20

    def set_effects(self, defender):
        do_stun = False
        message = None

        amount_of_poison = 0
        for effect in self.effects:
            match effect:
                case "poisoned":
                    if defender.knife:
                        knife_damage = 1
                    else:
                        knife_damage = 0
                    if self.EN == 1 + knife_damage:
                        self.EN = self.EN - 1 - knife_damage
                        amount_of_poison += 1 + knife_damage
                    elif self.EN != 0:
                        self.EN = self.EN - 2 - knife_damage
                        amount_of_poison += 2 + knife_damage
                    
                case "do_stun":
                    do_stun = True
                    self.abilities.remove('do_stun')
        if amount_of_poison != 0:
            message = f". {self.combatant} lost {amount_of_poison} EN from poisoning"

        return do_stun, message

    def get_if_dodge(self, defender: object):
        """
        Return boolean
        """
        doDodge = False
        if defender.dodge:
            if self.SP <= defender.SP and defender.EN > 0:
                if 1 == random.randint(1, 5):
                    doDodge = True
            elif 1 == random.randint(1,20):
                doDodge = True
        return doDodge

    def get_if_focus(self, defender: object):
        """
        Return boolean
        """
        if self.temp_focus:
            self.perm_focus = True
            self.temp_focus = False
            return True
        elif self.perm_focus and 1 == random.randint(1,10):
            return True
        else:
            return False

    def set_take_abilities(self, defender: object):
        """
        Remove some abilities on EN 0
        """
        if self.EN <= 0:
            for effect in self.effects:
                match effect:
                    case 'dodge':
                        self.effects.remove('dodge')
                    case 'guard':
                        self.effects.remove('guard')
                    case 'mount':
                        self.effects.remove('has_mount')
                    case 'resist':
                        self.effects.remove('resist')

        if defender.EN <= 0:
            for effect in defender.effects:
                match effect:
                    case 'dodge':
                        defender.effects.remove('dodge')
                    case 'guard':
                        defender.effects.remove('guard')
                    case 'mount':
                        defender.effects.remove('has_mount')
                    case 'resist':
                        defender.effects.remove('resist')



    ############

    def attack(self, defender: object):
        """
        Damage is (attack - (opponents defence + opponents armour)) + intelligence
        Cannot go below 0 for that first bracket
        Sets the damage to the other player's HP
        Returns message on what the action was
        """
        doDodge = self.get_if_dodge(defender)
        if doDodge:
            return True, f"{defender.combatant} dodged the attack"

        doFocus = self.get_if_focus(defender)
        my_focus_damage = 0
        my_focus_message = ''
        if doFocus:
            my_focus_damage = defender.AT / 2
            my_focus_message = ' critically'

        thats_alotta_damage = int(self.AT - (defender.DF + defender.AR) + my_focus_damage)
        if thats_alotta_damage < 0:
            thats_alotta_damage = 0

        if 'resist' not in defender.effects:
            thats_alotta_damage += self.IN

        if 'guard' not in defender.effects:
            defender.HP = defender.HP - thats_alotta_damage
        else:
            defender.AR = defender.AR - thats_alotta_damage
            if defender.AR <= 0:
                defender.AR = 0
                defender.effects.remove('guard')

        return True, f"{defender.combatant} was{my_focus_message} hit for {thats_alotta_damage} HP"

    def wait(self, defender):
        """Passes your turn"""
        return True, f"{self.combatant} passed their turn"

    def buff(self, defender):
        """
        Buff DF stat by 2 levels to the current player
        """
        fail_message = self.get_en_cost()
        if fail_message:
            return False, fail_message

        unit = 2 * 10
        stat = "DF"

        self.DF += unit

        self.set_damage_to_en()
        return True, f"{self.combatant} buffed {stat} to {unit}"

    def heal(self, defender):
        """
        Heals 100 HP to the current player
        """
        fail_message = self.get_en_cost()
        if fail_message:
            return False, fail_message

        healing = 100
        self.HP = self.HP + healing

        self.set_damage_to_en()
        return True, f"{self.combatant} healed for {healing} HP"

    def jog(self, defender):
        """
        Increase movement speed by 1 to the current player, and can only be used once
        """
        fail_message = self.get_en_cost()
        if fail_message:
            return False, fail_message

        self.SP += 1 * 5

        self.set_damage_to_en()
        return True, f"{self.combatant} raised SP by 5"

    def mount(self, defender):
        """
        Ride atop a mount, giving you increased movement speed by 1 to the current player,
        and boosting AT, DF, SP by 1. 
        """
        fail_message = self.get_en_cost()
        if fail_message:
            return False, fail_message

        self.effects.append("mount")

        self.set_damage_to_en()
        return True, f"{self.combatant} used mount"

    def warp(self, defender):
        """
        Call upon the (Un/)Holiest magic and increase each offensive and defensive stat by 1
        Costs 10 Endurance
        """
        fail_message = self.get_en_cost(10)
        if fail_message:
            return False, fail_message

        self.AT += 20
        self.IN += 10
        self.DF += 10
        self.AR += 20
        self.HP += 10

        self.set_damage_to_en(10)
        return True, f"{self.combatant} used warp on themselves."

    def focus(self, defender):
        """
        Gain the Focused status, for next turn only add +2 AT to the current player
        gain a 10% crit chance, and attack with one of your weapons as you focus, dealing 50 untouched damage as well as any other effects.
        """
        fail_message = self.get_en_cost()
        if fail_message:
            return False, fail_message

        self.set_damage_to_en()

        if 'focus' not in self.effects:
            self.effects.append("focused")
            self.temp_focus = True

            return True, f"{self.combatant} gained the focus effect for the next round, and a permanent chance to cause crit damage."
        else:
            return True, f"{self.combatant} gained the focus effect for the next round again, and a permanent chance to cause crit damage. "

    def poison(self, defender):
        """
        Drain EN by 2 to the other player, increasing with each stack
        """
        fail_message = self.get_en_cost()
        if fail_message:
            return False, fail_message

        doDodge = self.get_if_dodge(defender) # Dodge
        if doDodge:
            return True, f"{defender.combatant} dodged the poison attempt"

        self.set_damage_to_en()

        if "poison" not in defender.effects:
            defender.effects.append("poisoned")
            return True, f"{defender.combatant} has been poisoned"
        else:
            defender.effects.append("poisoned")
            return True, f"{defender.combatant} has been poisoned again"

    def stun(self, defender):
        """
        25% chance to cause Stunned status effect 
        """
        fail_message = self.get_en_cost()
        if fail_message:
            return False, fail_message

        doDodge = self.get_if_dodge(defender) # Dodge
        if doDodge:
            return True, f"{defender.combatant} dodged the attack"

        doFocus = self.get_if_focus(defender) # Check for focus damage
        my_focus_damage = 0
        my_focus_message = ''
        if doFocus:
            my_focus_damage = defender.AT / 2
            my_focus_message = ' critically'

        # Get damage
        thats_alotta_damage = int(self.AT - (defender.DF + defender.AR) + my_focus_damage)
        if thats_alotta_damage < 0:
            thats_alotta_damage = 0

        if 'resist' not in defender.effects:
            thats_alotta_damage += self.IN

        # Do damage
        defender.HP = defender.HP - thats_alotta_damage
        message =  f"{defender.combatant} was{my_focus_message} hit for {thats_alotta_damage} HP"

        self.set_damage_to_en()

        # Get if stunned
        myRoll = random.randint(1,5)
        if myRoll == 1:
            message += f". {self.combatant} has been stunned"
            self.abilities.append('do_stun')
            return True, message

        else:
            message += f". The stun failed"
            return True, message

    def explode(self, defender):
        """
        Attack with the combined strength of your AT and IN
        against your opponent's speed instead of their defence.
        Has a range of Across, decreasing in damage by 50% per extra space
        """
        fail_message = self.get_en_cost(8)
        if fail_message:
            return False, fail_message

        doFocus = self.get_if_focus(defender) # Check for focus damage
        my_focus_damage = 0
        my_focus_message = ''
        if doFocus:
            my_focus_damage = defender.AT / 2
            my_focus_message = ' critically'

        thats_alotta_damage = int((self.AT + self.IN) - ( defender.SP ) + my_focus_damage)
        if thats_alotta_damage < 0:
            thats_alotta_damage = 0

        if 'resist' not in defender.effects:
            thats_alotta_damage += self.IN

        defender.HP = defender.HP - thats_alotta_damage

        self.set_damage_to_en(8)
        return True, f"{defender.combatant} was{my_focus_message} hit for {thats_alotta_damage} HP"

    def strip(self, defender):
        """
        remove enemy's AR equal to your intelligence,
        reduce your intelligence by the same amount 
        This move cannot be stacked
        """
        fail_message = self.get_en_cost()
        if fail_message:
            return False, fail_message

        if "stripped" in defender.effects:
            return False, f"{defender.combatant} was already stripped and misses a turn"
        else:
            self.effects.append("stripped")

            amount = self.IN

            defender.AR = defender.AR - amount
            if defender.AR <= 0:
                defender.AR = 0

            self.IN = self.IN - amount
            if self.IN <= 0:
                self.IN = 0

        self.set_damage_to_en()
        return True, f"{self.combatant} lost {amount} IN, {defender.combatant} lost {amount} AR"

    def steal(self, defender):
        """
        Take a random status from the opponent - and replace it with a wound status.
        """
        fail_message = defender.get_en_cost()
        if fail_message:
            return False, fail_message

        doDodge = self.get_if_dodge(defender) # Dodge
        if doDodge:
            return True, f"{defender.combatant} dodged the attack"

        q = random.randint(1, 6)
        stat = ""
        amount = 0
        if defender.AR > 20 and q==1:
            amount = 20
            stat = "AR"
            self.AR += amount
            defender.AR = defender.AR - amount
        elif defender.DF > 10 and q==2:
            amount = 10
            stat = "DF"
            self.DF += amount
            defender.DF = defender.DF - amount
        elif defender.SP > 5 and q==3:
            amount = 5
            stat = "SP"
            self.SP += amount
            defender.SP = defender.SP - amount
        elif defender.EN > 10 and q==4:
            amount = 10
            stat = "EN"
            self.EN += amount
            defender.EN = defender.EN - amount
        elif defender.AT > 20 and q==5:
            amount = 20
            stat = "AT"
            self.AT += amount
            defender.AT = defender.AT - amount
        elif defender.IN > 10 and q==6:
            amount = 10
            stat = "IN"
            self.IN += amount
            defender.IN = defender.IN - amount
        else:
            amount = 15
            stat = "HP"
            self.HP += amount
            defender.HP = defender.HP - amount        

        self.set_damage_to_en()
        return True, f"{self.combatant} stole {amount} {stat}"

    #####

    def set_myclass(self):
        # Rogue
        # Endurance must be more than double your Armour.
        # Must have a speed stat higher than the opponent

        # Fortress Guard
        # Must have above 7 in Armour.

        # Weapons Expert
        # Must have an Intelligence stat of 8 or above.

        # Assassin
        # Speed must be more than double your defence. Ex. Df 2, sp 5/ df 4, sp 9

        # Titan
        # Defense must be more than double attack.
        # Ex: at 1, df 3/ at 3, df 7

        # Martial artist
        # Armour and Intelligence combined must be a total of 8.
        # Ex. 4 ar, 4 in/ 8 ar/ 8 in

        # Mage
        # Your Intelligence stat must be double your Attack stat.
        # Ex. 2 at, 4 in/ 4 at, 8 In

        pass