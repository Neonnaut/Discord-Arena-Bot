import discord
from discord.ext import commands

from constants import CHECK, DEFAULT_PROFILE_PICTURE

from .arena.arena import (
    OpenModal, format_player_info_embed, generate_arena_info_embed,
    get_combatant, get_combatants_for_arena, set_winner)
from .arena.arena_match import ArenaMatch

class Games(commands.Cog, name="games"):
    """Games like Arena."""
    COG_EMOJI = "🕹️"

    def __init__(self, bot: discord.Client):
        self.bot:discord.Client = bot

    @commands.hybrid_command(description="A 1v1 RPG : set | @<challengee> | <action> | quit | help.")
    @discord.app_commands.describe(action="@<challengee>, <action>, quit, or help.")
    @commands.guild_only()
    async def arena(
        self,
        ctx: commands.Context,
        *,
        action: str
    ):
        """
        Play a 1 v 1 RPG battle with another user.
        You can read the rules on how to play and detailed instructions [here](https://docs.google.com/document/d/1t5jYRG5n4GWRP1jWrHiHjxPoJQfH3dbX6OrQbOQUA3k).
        """
        if action in ['info','help']:
            return await ctx.reply(embed=generate_arena_info_embed(ctx.clean_prefix), mention_author=False, ephemeral=False)
        elif action in  ['set','set_combatant','make']:
            return await ctx.send('Set your combatant!\nThis button can be used multiple times but times out after two hours', view=OpenModal(timeout=7200))
        elif action in  ['quit','reset','concede','surrender']:
            ## Reset the arena
            if len(self.arena_matches) != 0:
                self.arena_matches.remove(self.arena_matches[0])
                return await ctx.send(f"The Arena has been reset. The game has ended.")
            else:
                return await ctx.send(f"There are no arena matches playing.")                
        elif action.startswith("<@") and action.endswith(">"):
            ## Challenge another user
            try:
                challengee = await commands.MemberConverter().convert(ctx, action)
            except:
                return await self.bot.send_warning(ctx, "I could not find that user.")
            
            if len(self.arena_matches) != 0:
                return await self.bot.send_warning(ctx, "An arena match is already running.")
            if challengee.bot:
                return await self.bot.send_warning(ctx, "You cannot challenge bots.")
            """
            if challengee == ctx.message.author:
                await self.bot.send_warning(ctx, "You cannot challenge yourself.")
                return
            """

            # Get the combatants
            async with ctx.typing():
                combatants, message = await get_combatants_for_arena(
                    [ctx.message.author, challengee]
                )
                if combatants == None:
                    return await self.bot.send_warning(ctx, message)
                player1_stats = combatants[0]
                player2_stats = combatants[1]

                if challengee.id == ctx.message.author.id:
                    player2_stats = [ctx.message.author.id, ctx.message.author.display_name, 'Test Opponent', '3', '5', '2', '2', '3', '4', '2', '0', 'poison', 'dodge', 'knife', DEFAULT_PROFILE_PICTURE]

                # Create the match
                # MAGIC STARTS HERE
                match = ArenaMatch(player1_stats, player2_stats)
                self.arena_matches.append(match)

                ArenaEmbed = match.print_board()

                return await ctx.send(f'{CHECK} An arena match has begun\n"{match.player_1.combatant}" played by {match.player_1.username}' + \
                    f' Vs "{match.player_2.combatant}" played by {match.player_2.username}.', embed=ArenaEmbed)
        
        elif action.split(' ')[0] == 'show' and len(action.split(' ')) == 2:
            try:
                challengee = await commands.MemberConverter().convert(ctx, action.split(' ')[1])
            except:
                return await self.bot.send_warning(ctx, "I could not find that user.")
            async with ctx.typing():
                data, message = await get_combatant(challengee)
                if not data:
                    return await self.bot.send_warning(ctx, message)
                else:
                    data.update({"url":'https://docs.google.com/spreadsheets/d/1JEwnfr0EWAltG9QdXzfox5ujuaaFhbtPWLUFH4kovhs/#gid=2024359291'})
                    embed = format_player_info_embed(data)
                    return await ctx.send(message, embed=embed)
        else:
            ### Else interpret action as an action
            # MAGIC STARTS HERE
            try:
                myMatch = self.arena_matches[0]
            except:
                return await self.bot.send_warning(ctx, "There are no arena matches running.")

            # Check if it is the evokers turn
            if myMatch.current_player.userID == ctx.message.author.id:
                # Try and make the move
                mySuccess = await myMatch.make_move(action)
                if mySuccess:
                    embed = myMatch.print_board()
                    await ctx.send(embed=embed)
                    # Check if match over and end match if so
                    if myMatch.end_result != "":
                        self.arena_matches.remove(self.arena_matches[0])
                        await set_winner(myMatch.winner)
                else:
                    return await self.bot.send_warning(ctx, str(myMatch.last_move))
            else:
                return await self.bot.send_warning(ctx, "It is not your turn.")

async def setup(bot: commands.bot):
    await bot.add_cog(Games(bot))