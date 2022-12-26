import random
from discord import Embed

from cogs.arena.arena_player import Player

from constants import INFO, CHECK

class ArenaMatch:
    def __init__(self, player_1_stats, player_2_stats):
        self.player_1 = Player(player_1_stats)
        self.player_2 = Player(player_2_stats)

        # Make the player with the most speed go first
        if self.player_1.SP > self.player_2.SP:
            self.current_player = self.player_1
            self.other_player = self.player_2
        else:
            self.current_player = self.player_2
            self.other_player = self.player_1

        self.last_move = ""
        self.end_result = ""
        self.winner = None

    def make_move(self, move):
        """
        Makes a move
        Returns Bool whether the action was successful, and a message
        """
        move = move.casefold()
        match move: # Move aliases
            case 'attck' | 'a':
                move = 'attack'
            case 'pass':
                move = 'wait'

        # Get the move
        move_functions = [a for a in dir(self.player_1) if not a.startswith('__') and not a.startswith('set') and not a.startswith('get') and callable(getattr(self.player_1, a))]
        if move not in move_functions:
            self.last_move = "That is not a valid move"
            return False

        if move not in self.current_player.abilities:
            if move != 'attack' and move != 'wait':
                self.last_move = "That is not one of your moves"
                return False


        # Do the move
        my_function = getattr(self.current_player, move, lambda: None)
        success, message = my_function(self.other_player)

        # On failure
        if not success:
            self.last_move = message
            return False

        # On success
        self.last_move = message

        is_stunned, stat_message = self.current_player.set_effects(
            self.other_player
        )
        if not is_stunned:
            self.change_turn()
        if stat_message:
            self.last_move += f'{stat_message}'

        self.current_player.set_take_abilities(
            self.other_player
        )
            
        self.match_won()
        return True

    def calculate_effects(self):
        """
        Calculate the effects on player 1 and 2
        """
        pass

    def change_turn(self):
        """
        Changes the current player to the other player
        Changes the other player to the current player
        returns: None
        """
        if self.current_player == self.player_1:
            self.current_player = self.player_2
            self.other_player = self.player_1
        else:
            self.current_player = self.player_1
            self.other_player = self.player_2

    def print_board(self) -> Embed:
        """
        Returns the arena board as an embed with each players
        EN, Health, and effects
        """
        embed = Embed(
            title=f"Arena"
        )

        myDescription = []
        if self.last_move != "":
            myDescription.append(f"{INFO} {self.last_move}")

        if self.end_result == "":
            myDescription.append(f"{INFO} It is {self.current_player.combatant}'s turn now")
        else:
            myDescription.append(f"{CHECK} {self.end_result}")

        embed.description="\n".join(myDescription)
        
        embed.add_field(
            inline=True,
            name=f"**{self.player_1.combatant}**",
            value=f"HP:`{self.player_1.HP}`, EN:`{self.player_1.EN}`," + \
            f" DF:`{self.player_1.DF}`, AR:`{self.player_1.AR}`," + \
            f"\nAT:`{self.player_1.AT}`, IN:`{self.player_1.IN}`," + \
            f" SP:`{self.player_1.SP}`" + \
            f"\nWeapon:`{self.player_1.weapon}`"
            f"\nAbilities:`{', '.join(self.player_1.abilities) or 'none'}`"
            f"\nStatuses:`{', '.join(self.player_1.effects) or 'none'}`"
        )

        embed.add_field(
            inline=True,
            name="Vs",
            value="\u200b"
        )
        #```elm\nA b _ _```

        embed.add_field(
            inline=True,
            name=f"**{self.player_2.combatant}**",
            value=f"HP:`{self.player_2.HP}`, EN:`{self.player_2.EN}`," + \
            f" DF:`{self.player_2.DF}`, AR:`{self.player_2.AR}`," + \
            f"\nAT:`{self.player_2.AT}`, IN:`{self.player_2.IN}`," + \
            f" SP:`{self.player_2.SP}`" + \
            f"\nWeapon:`{self.player_2.weapon}`"
            f"\nAbilities:`{' '.join(self.player_2.abilities) or 'none'}`"
            f"\nStatuses:`{' '.join(self.player_2.effects) or 'none'}`"
        )

        embed.set_author(
            name=f"{self.current_player.combatant} ({self.current_player.username})",
            icon_url=self.current_player.image
        )

        return embed

    def match_won(self):
        """
        Check if the match has been won by a player
        If a combatant is dead, return the winning
        """
        if self.player_1.HP <= 0:
            self.end_result = f"{self.player_2.combatant} has won this match"
            self.winner = self.player_2.userID
        elif self.player_2.HP <= 0:
            self.end_result = f"{self.player_1.combatant} has won this match"
            self.winner = self.player_1.userID



    