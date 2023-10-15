# Imports
import asyncio
import random
import discord
import datetime
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import GroupCog
from discord.app_commands import Group, command

def convert(time):
    pos = ["s","m","h","d"]

    time_dict = {"s" : 1, "m" : 60, "h" : 3600, "d": 86400}

    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

msg_ = None

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Confirming...', ephemeral=True)
        self.value = True
        button.disabled=True
        self.confirm.disabled = True
        self.cancel.disabled = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling...', ephemeral=True)
        button.disabled=True
        self.value = False
        self.cancel.disabled = True
        self.confirm.disabled = True
        self.stop()


class Enter(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.reacted = []
        self.entries = discord.ui.Button(
            label="Number of Entries: 0",
            style=discord.ButtonStyle.secondary,
            disabled=True,
            emoji='<:people:1084437638431383594>'
        )
        self.add_item(self.entries)

    global msg_
    
    @discord.ui.button(
        label="Enter",
        style=discord.ButtonStyle.green,
        emoji="<a:g_tada:1051439295774326874>"
    )
    async def enter(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id in self.reacted:
            em = discord.Embed(
                description="You've already entered the giveaway!",
                color=discord.Colour.from_rgb(255, 0, 0),
                timestamp=datetime.datetime.now()
            )
            em.set_author(
                name=f"{interaction.user.name}#{interaction.user.discriminator}",
                icon_url=f'{interaction.user.avatar.url}'
            )
            leave = Leave()
            await interaction.response.send_message(
                embed=em,
                ephemeral=True,
                view=leave
            )
        else:
            self.reacted.append(interaction.user.id)
            self.entries.label = f"Number of Entries: {len(self.reacted)}"
            await msg_.edit(embed=msg_.embeds[0], view=self)
            
            em1 = discord.Embed(
                timestamp=datetime.datetime.now(),
                description="Successfully entered the giveaway!",
                color=discord.Colour.green()
            )
            em1.set_author(
                name=f"{interaction.user.name}#{interaction.user.discriminator}",
                icon_url=f'{interaction.user.avatar.url}'
            )
            await interaction.response.send_message(
                embed=em1,
                ephemeral=True
            )
            
class Leave(discord.ui.View):
    def __init__(self):
        super().__init__()
    
    
    @discord.ui.button(
        label='Leave Giveaway',
        style=discord.ButtonStyle.danger
    )
    async def leave(self, interaction: discord.Interaction, button: discord.Button):
        enter = Enter()
        if len(enter.reacted) > 0:
            enter.reacted.pop(interaction.user.id)
            em = discord.Embed(
                description="Successfully left the giveaway!",
                color=discord.Color.red()
            )
            em.set_author(
                name=f"{interaction.user.name}#{interaction.user.discriminator}",
                icon_url=f'{interaction.user.avatar.url}'
            )
            await interaction.response.send_message(embed=em, ephemeral=True)
        else:
            em = discord.Embed(
                description="Already left the giveaway!",
                color=discord.Color.red()
            )
            em.set_author(
                name=f"{interaction.user.name}#{interaction.user.discriminator}",
                icon_url=f'{interaction.user.avatar.url}'
            )
            await interaction.response.send_message(embed=em, ephemeral=True)

class Giveaway(commands.GroupCog, name="giveaway"):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.prize = None
        self.duration = None
        self.winners = None
        self.role = None
        self.end_time = None
        self.ended = False

        super().__init__()

    @app_commands.command(name="create", description="Create a new giveaway with customisable requirements!")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.describe(
        channel="Channel to create the giveaway in.",
        prize="Prize to be given away.",
        duration="Duration of the giveaway. [s|m|h|d]",
        winners="Number of winners.",
        role="Required role to enter the giveaway."
    )
    async def create(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        prize: str,
        duration: str,
        winners: int = None,
        role: discord.Role = None
    ):
        self.channel = channel
        self.prize = prize
        self.duration = duration
        self.winners = winners
        self.role = role

        global msg_
        time = convert(duration)
        if not winners:
            winners = 1
        
        em = discord.Embed(
            title="Creating new giveaway",
            color=discord.Color.from_rgb(255, 0, 0),
            timestamp=datetime.datetime.now()
        )
        em.add_field(name="Channel", value=f"{channel.mention}")
        em.add_field(name="Prize", value=f"{prize}")
        em.add_field(name="Duration", value=f"{duration}")
        em.add_field(name="Winners", value=f"{winners}")
        em.add_field(name="Role required", value=f"{role.mention if role else 'None'}")

        current_time = datetime.datetime.now()  # Get the current time
        end_time = current_time + datetime.timedelta(seconds=time)  # Calculate the end time
        end_time_unix = int(end_time.timestamp())
        self.end_time = end_time_unix
        view = Confirm()
        await interaction.response.send_message(content="Do you want to create this giveaway?", embed=em, view=view)
        emoji = self.bot.get_emoji(1051439295774326874)
        gw = discord.Embed(
            title=f"{prize}", 
            description=f"Click on the button to enter! \n:alarm_clock: Ends <t:{end_time_unix}:R> from now.",
            color=discord.Color.from_rgb(255, 0, 0),
            timestamp=datetime.datetime.now()
        )
        gw.add_field(name=":medal: Winners", value=f"{winners}")
        gw.add_field(name=":crown: Role required", value=f"{role.mention}" if role else "None")
        gw.set_footer(text=f"Hosted by {interaction.user.name}#{interaction.user.discriminator}", icon_url=f'{interaction.user.avatar.url}')
        await view.wait()
        button = Enter()
        if view.value is None:
            await interaction.followup.send('Timed out!')
        elif view.value:
            await interaction.followup.send("Created!")
        
            msg = await channel.send(content=f'{emoji} New Giveaway {emoji}', embed=gw, view=button)
            msg_ = msg

            await asyncio.sleep(time)

            reactants = button.reacted
            reacts = []
            for h in reactants:
                member = interaction.guild.get_member(h)
                reacts.append(member.mention)
            embed = discord.Embed(
                title="Entries",
                description=f"\n".join(reacts),
                color=discord.Color.from_str('#2b2d31'),
                timestamp=datetime.datetime.now()
            )
            edited_gw = discord.Embed(
                title=f"{prize}",
                description=f"This giveaway has ended. \n:alarm_clock: Ended <t:{end_time_unix}:R>.",
                color=discord.Color.from_rgb(255, 0, 0),
                timestamp=datetime.datetime.now()
            )
            edited_gw.add_field(name=":medal: Winners", value=f"{winners}")
            edited_gw.add_field(name=":crown: Role required", value=f"{role.mention}" if role else "None")
            edited_gw.set_footer(text=f"Hosted by {interaction.user.name}#{interaction.user.discriminator}", icon_url=f'{interaction.user.avatar.url}')
            await msg.edit(
                content=f"{emoji} Giveaway Ended {emoji}",
                embeds=[edited_gw, embed],
                view=button
            )
            self.ended = True
            
            if len(reactants) > 0:
                if role:
                    reactants_users = []
                    for i in reactants:
                        m = interaction.guild.get_member(i)
                        if role not in m.roles:
                            reactants_users.pop(i)
                        else:
                            reactants_users.append(m)

                    gw_winners = random.choices(reactants_users, k=min(winners, len(reactants_users)))
                    list1 = []
                    for user in gw_winners:
                        list1.append(user.mention)
                    if list1:
                        em = discord.Embed(
                            title="Giveaway winners",
                            description=f"Congratulations on winning the **[{prize}]({msg.jump_url})**!",
                            color=discord.Color.from_str('#2b2d31'),
                            timestamp=datetime.datetime.now()
                        )
                        
                        await channel.send(
                            content=f"{', '.join(list1)}" if len(list1) > 1 else f"{list1[0]}",
                            embed=em
                        )
                    list1.clear()
                elif not role:
                    users = []
                    for i in reactants:
                        m = interaction.guild.get_member(i)
                        users.append(m)
                    gw_wins = random.choices(users, k=min(winners, len(users)))
                    list2 = []
                    for user in gw_wins:
                        list2.append(user.mention)
                    if list2:
                        em = discord.Embed(
                            title="Giveaway winners",
                            description=f"Congratulations on winning the **[{prize}]({msg.jump_url})**!",
                            color=discord.Color.from_str('#2b2d31'),
                            timestamp=datetime.datetime.now()
                        )
                        await channel.send(
                            content=f"{', '.join(list2)}" if len(list2) > 1 else f"{list2[0]}",
                            embed=em
                        )
                    list2.clear()
            else:
                await channel.send(
                    content=f"No one entered the giveaway :("
                )

        else:
            await interaction.followup.send("Cancelled!")

    @app_commands.command(name='end', description="End an on-going giveaway.")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.describe(
        channel="Giveaway channel.",
        id="ID of the giveaway.",
        winners="Number of winners."
    )
    async def end(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        id: str,
        winners: int
    ):
        if not self.ended:
            reactants = button.reacted
            reacts = []
            for h in reactants:
                member = interaction.guild.get_member(h)
                reacts.append(member.mention)
            embed = discord.Embed(
                title="Entries",
                description=f", ".join(reacts),
                color=discord.Colour.dark_theme(),
                timestamp=datetime.datetime.now()
            )
            await channel.send(embed=embed)
            prize = self.prize
            role = self.role
            end_time = self.end_time
            try:
                msg = await channel.fetch_message(id)
            except discord.errors.NotFound or discord.errors.Forbidden:
                await interaction.response.send_message(
                    "Invalid message ID!",
                    ephemeral=True
                )
            emoji = self.bot.get_emoji(1051439295774326874)
            em = discord.Embed(
                title=f'{prize}',
                description=f"This giveaway has ended. \n:alarm_clock: Ended <t:{end_time}:R>.",
                color=discord.Color.from_rgb(255, 0, 0)
            )
            em.add_field(name=":medal: Winners", value=f"{winners}")
            em.add_field(name=":crown: Role required", value=f"{role.mention}" if role else "None")
            button = Enter()
            button.enter.disabled = True
            await msg.edit(
                content=f"{emoji} Giveaway Ended {emoji}",
                embed=em,
                view=button
            )
            reactants = button.reacted
            if len(reactants) > 0:
                if role:
                    reactants_users = []
                    for i in reactants:
                        m = interaction.guild.get_member(i)
                        if role in m.roles:
                            await reactants_users.append(m)
                        
                    
                    gw_winners = random.choices(reactants_users, k=winners)
                    list1 = []
                    for user in gw_winners:
                        list1.append(user.mention)
                    if list1:
                        em = discord.Embed(
                            title="Giveaway winners",
                            description=f"Congratulations on winning the **[{prize}]({msg.jump_url})**!",
                            color=discord.Color.from_str('#2b2d31'),
                            timestamp=datetime.datetime.now()
                        )
                        await channel.send(
                            content=f"{', '.join(list1)}" if len(list1) > 1 else f"{list1[0]}",
                            embed=em
                        )
                    list1.clear()
                elif not role:
                    reactors = button.reacted
                    users = []
                    for i in reactors:
                        m = interaction.guild.get_member(i)
                        await users.append(m)
                    
                    gw_wins = random.choices(users, k=winners)
                    list2 = []
                    for user in gw_wins:
                        list2.append(user.mention)
                    if list2:
                        em = discord.Embed(
                            title="Giveaway winners",
                            description=f"Congratulations on winning the **[{prize}]({msg.jump_url})**!",
                            color=discord.Color.from_str('#2b2d31'),
                            timestamp=datetime.datetime.now()
                        )
                        await channel.send(
                            content=f"{', '.join(list2)}" if len(list2) > 1 else f"{list2[0]}",
                            embed=em
                        )
                    list2.clear()
        else:
            await interaction.response.send_message(
                "This giveaway has already ended!",
                ephemeral=True
            )
    

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
