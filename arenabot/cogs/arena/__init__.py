import discord
from discord.ext import commands

from constants import ERR, CHECK, WARN, INFO

from cogs.arena.arena import (
    OpenModal,
    get_combatant,
    generate_arena_info_embed,
    set_winner,
    format_player_info_embed,
    get_combatants_for_arena
)

from cogs.arena.arena_match import (
    ArenaMatch
)

class Arena(commands.Cog, name="arena"):
    """Commands for the arena minigame."""

    COG_EMOJI = "🏟️"

    def __init__(self, bot):
        self.bot = bot

        self.arena_matches = []

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
        match action:
            case "set" | "set_combatant" | "make":
                ## Make set combatant button
                await ctx.send('Set your combatant!\nThis button can be used multiple times but times out after two hours', view=OpenModal(timeout=7200))
            case "quit" | "reset" | "concede" | "surrender":
                ## Reset the arena
                if len(self.arena_matches) != 0:
                    self.arena_matches.remove(self.arena_matches[0])
                    await ctx.send(f"The Arena has been reset. The game has ended.")
                else:
                    await ctx.send(f"There are no arena matches playing.")
            case None | "info" | "help":
                ## Show help embed
                await ctx.reply(embed=generate_arena_info_embed(ctx.clean_prefix), mention_author=False, ephemeral=False)
            case _:
                if action.startswith("<@"):
                    ## Challenge another user
                    try:
                        challengee = await commands.MemberConverter().convert(ctx, action)
                    except:
                        await ctx.send(f"{ERR} I could not find that user.", delete_after=5)
                        try:
                            await ctx.message.delete(delay=5)
                        except Exception:
                            pass
                    else:
                        if len(self.arena_matches) != 0:
                            await ctx.send(f"{ERR} An arena match is already running.", delete_after=5)
                            try:
                                await ctx.message.delete(delay=5)
                            except Exception:
                                pass
                            return
                        if challengee.bot:
                            await ctx.send(f"{ERR} You cannot challenge bots.", delete_after=5)
                            try:
                                await ctx.message.delete(delay=5)
                            except Exception:
                                pass
                            return
                        """
                        if challengee == ctx.message.author:
                            await ctx.channel.send(f"{ERR} You cannot challenge yourself.", delete_after=5)
                            try:
                                await ctx.message.delete(delay=5)
                            except Exception:
                                pass
                            return
                        """

                        # Get the combatants
                        async with ctx.typing():
                            combatants, message = await get_combatants_for_arena(
                                [ctx.message.author, challengee]
                            )
                            if combatants == None:
                                await ctx.send(f'{ERR} {message}')
                                return
                            player1_stats = combatants[0]
                            player2_stats = combatants[1]

                            if challengee.id == ctx.message.author.id:
                                player2_stats = [ctx.message.author.id, ctx.message.author.display_name, 'Gitanas Nausėda', '3', '5', '2', '2', '3', '4', '2', '0', 'poison', 'guard', 'knife', 'https://cdn.discordapp.com/attachments/959751548232138792/1043261840903389275/unknown.png']

                            # Create the match
                            # MAGIC STARTS HERE
                            match = ArenaMatch(player1_stats, player2_stats)
                            self.arena_matches.append(match)

                            ArenaEmbed = match.print_board()

                            await ctx.send(f'{CHECK} An arena match has begun\n"{match.player_1.combatant}" played by {match.player_1.username}' + \
                                f' Vs "{match.player_2.combatant}" played by {match.player_2.username}.', embed=ArenaEmbed)

                else:
                
                    ### Else interpret action as an action
                    # MAGIC STARTS HERE
                    try:
                        myMatch = self.arena_matches[0]
                    except:
                        await ctx.send(f"{ERR} There are no arena matches running.", delete_after=5)
                        try:
                            await ctx.message.delete(delay=5)
                        except Exception:
                            pass
                    else:
                        # Check if it is the evokers turn
                        if myMatch.current_player.userID == ctx.message.author.id:
                            # Try and make the move
                            mySuccess = myMatch.make_move(action)
                            if mySuccess:
                                embed = myMatch.print_board()
                                await ctx.send(embed=embed)
                                # Check if match over and end match if so
                                if myMatch.end_result != "":
                                    self.arena_matches.remove(self.arena_matches[0])
                                    await set_winner(myMatch.winner)
                            else:
                                await ctx.send(f"{WARN} {myMatch.last_move}", delete_after=5)
                                try:
                                    await ctx.message.delete(delay=5)
                                except Exception:
                                    pass
                        else:
                            await ctx.send(f"{ERR} It is not your turn.", delete_after=5)
                            try:
                                await ctx.message.delete(delay=5)
                            except Exception:
                                pass

    @commands.hybrid_command()
    @commands.guild_only()
    async def show_arena_combatant(
        self,
        ctx: commands.Context,
        *,
        username: discord.Member
    ):
        """Shows the combatant of a user if they have one."""
        # Show the combatant of a user
        async with ctx.typing():
            data, message = await get_combatant(username)
            if not data:
                await ctx.send(f"{ERR} {message}")
            else:
                data.update({"url":'https://docs.google.com/spreadsheets/d/1JEwnfr0EWAltG9QdXzfox5ujuaaFhbtPWLUFH4kovhs/#gid=2024359291'})
                embed = format_player_info_embed(data)
                await ctx.send(message, embed=embed)

async def setup(bot: commands.bot):
    await bot.add_cog(Arena(bot))