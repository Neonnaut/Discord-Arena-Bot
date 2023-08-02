import time
from typing import Optional
import discord
from discord import Embed

from constants import GSHEETS_KEY, ERR, WARN, CHECK, INFO, DIAMOND

from ..arena.gsheet_client import Arena_Schema

Arena_schema = Arena_Schema("1JEwnfr0EWAltG9QdXzfox5ujuaaFhbtPWLUFH4kovhs","Arena")

ABILITIES =['buff', 'heal', 'poison', 'strip', 'summon', 'mount', 'stun', 'explosion', 'focus', 'steal', 'jog', 'dodge', 'warp', 'resist', 'guard']

WORKBOOK_KEY = "1JEwnfr0EWAltG9QdXzfox5ujuaaFhbtPWLUFH4kovhs"
WORKSHEET = "Arena"

Arena_Schema  = Arena_Schema("1JEwnfr0EWAltG9QdXzfox5ujuaaFhbtPWLUFH4kovhs","Arena")

# Define a View that gives us a button
class OpenModal(discord.ui.View):
    #def __init__(self, timeout: Optional[float] = 5):
        #super().__init__(timeout=timeout)

    # note: The name of the function does not matter to the library
    @discord.ui.button(label='Set Combatant', style=discord.ButtonStyle.green)
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):

        # Send a the Combatant modal as part of the interaction
        await interaction.response.send_modal(Combatant())

    # remove dropdown from message on timeout
    async def on_timeout(self):
        #await self.message.edit(embed=self.summary, view=None)
        pass

class Combatant(discord.ui.Modal, title='Combatant'):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    combatant = discord.ui.TextInput(
        label='combatant',
        placeholder='Combatant name here',
        max_length=20,
    )

    stats = discord.ui.TextInput(
        label='Stats: AT IN DF AR HP SP EN Wins',
        placeholder='8 stats seperated by spaces. Max base stat of 21',
        max_length=21,
    )

    abilities = discord.ui.TextInput(
        label='Abilities',
        placeholder='Abilities, seperated by a space',
        max_length=20,
    )

    weapon = discord.ui.TextInput(
        label='Weapon',
        placeholder='',
        max_length=20,
    )

    image = discord.ui.TextInput(
        label='Image URL',
        placeholder='',
        max_length=30,
        required = False
    )

    async def on_submit(self, interaction: discord.Interaction):
        ping = time.time()

        combatant = self.combatant.value
        stats = self.stats.value
        stats = stats.split()
        if len(stats) == 7:
            stats.append("0")

        wins = stats.pop()

        abilities = self.abilities.value.casefold()
        abilities = abilities.split(" ")

        ab1 = abilities[0].strip()
        try:
            ab2 = abilities[1].strip()
        except:
            ab2 = ab1

        weapon = self.weapon.value.casefold()

        image = self.image.value

        message = None

        await interaction.response.send_message("Attempting to set your combatant...", ephemeral=True, delete_after=6)

        denied = True

        if wins.isdigit():
            if int(wins) >= 0:
                if ab1 in ABILITIES:
                    if ab2 in ABILITIES:
                        if len(stats) == 7:
                            if int(stats[4]) > 0:
                                stat_total = 0
                                for stat in stats:
                                    if stat.isdigit():
                                        stat_total += int(stat)
                                        denied = False
                                    else:
                                        denied = True
                                        message = f'Your stats were not digits.'
                                if stat_total > 21 + int(wins):
                                    denied = True
                                    message = f'Your total stats must be a maximum of 21 + your number of wins (artefacts).\n'\
                                        + f'In your case, a maximum total of `{21 + int(wins)}`, but you entered `{stat_total}`.'

                            else:
                                message = f'Your HP was at 0.'
                        else:
                            message = f'The number of stats was not eight.'
                    else:
                        message = f'That ability does not exist.'
                else:
                    message = f'That ability does not exist.'
            else:
                message = f'The number of wins was in the negatives.'
        else:
            message = f'The number of wins was not a number.'


        if not denied and not message:
            if image == '':
                output = [str(interaction.user.display_name), combatant] + stats + [wins] + [ab1, ab2, weapon, None]
            else:
                output = [str(interaction.user.display_name), combatant] + stats + [wins] + [ab1, ab2, weapon, image]
            
        ######
            myData, message = await Arena_Schema.set_combatant(
                interaction.user,
                output
            )
            if myData:
                myData.update({"url":'https://docs.google.com/spreadsheets/d/1JEwnfr0EWAltG9QdXzfox5ujuaaFhbtPWLUFH4kovhs/#gid=2024359291'})
                embed = format_player_info_embed(myData)
                ping = time.time() - ping
                embed.set_footer(text=f"Message Latency: {round(ping,1)}s")
                await interaction.followup.send(f"{CHECK} {message}", embed=embed, ephemeral=False)
            else:
                await interaction.followup.send(f"{ERR} {message}", ephemeral=False)
        else:
            ping = time.time() - ping
            await interaction.followup.send(f"{ERR} {message}", ephemeral=False)

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)

async def get_combatant(user):
    data, message = await Arena_Schema.show_combatant(user)
    return data, message

async def get_combatants_for_arena(users):
    data, message = await Arena_Schema.get_combatants_for_arena_match(users)
    return data, message

async def set_winner(userID):
    await Arena_Schema.set_winner(userID)

def format_player_info_embed(data: dict):

    embed = Embed()
    
    title = data.get("title")
    if title:
        embed.title = title

    author = data.get("author")
    if author:
        embed.set_author(name=author["name"], icon_url=author["icon_url"])

    description = data.get("description")
    if description:
        embed.description = description

    url = data.get("url")
    if url:
        embed.url = url

    fields = data.get("fields")
    if fields:
        set_field_1 = []
        set_field_2 = []
        for key, value in fields.items():
            for item in value:

                if len(set_field_1) < 7:
                    set_field_1.append(f"{DIAMOND}{item}")
                else:
                    set_field_2.append(f"{DIAMOND}{item}")

        if len(set_field_1) != 0:
            embed.add_field(
                inline=True,
                name=key,
                value='\n'.join(set_field_1)
            )
        if len(set_field_2) != 0:
            embed.add_field(
                inline=True,
                name='\u200b',
                value='\n'.join(set_field_2)
            )

    footer = data.get("footer")
    if footer:
        embed.set_footer(
            text=footer
        )

    image = data.get("image")
    if image:
        embed.set_image(
            url=image
        )

    return embed

def generate_arena_info_embed(prefix):

    embed = Embed(
        title=f"**Arena**",
        description="Play a 1 v 1 RPG battle with another user.\n"
        "You can read the rules on how to play and detailed instructions [here](https://docs.google.com/document/d/1t5jYRG5n4GWRP1jWrHiHjxPoJQfH3dbX6OrQbOQUA3k).",
        colour=discord.Colour.dark_green()
    )

    embed.add_field(
        inline=False,
        name=f"**Creating and viewing combatants**",
        value=
            f"`{prefix}arena set` - Creates a button for anyone to create or update their combatant."
            f"\n`{prefix}arena show <username>` - Displays a user's combatant."
    )

    embed.add_field(
        inline=False,
        name=f"**Starting and ending matches**",
        value=
            f"`{prefix}arena @<username>` - Starts an arena match against a user if they both have made a combatant."
            " This bot only runs one match at a time."
            f"\n`{prefix}arena quit` - Ends the match prematurely."
    )

    embed.add_field(
        inline=False,
        name=f"**Actions**",
        value=
            f"`{prefix}arena attack` - Attacks your opponent."
            f"\n`{prefix}arena <ability>` - Does one of your two abilities."
    )

    return embed

