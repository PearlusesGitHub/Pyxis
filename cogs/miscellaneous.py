import asyncio
from colorthief import ColorThief
import discord
from discord.ext import commands, tasks
import datetime
from discord import app_commands
from datetime import datetime
import time
from io import BytesIO
import requests
from PIL import Image
import typing

class Confirm(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()

class Miscellaneous(commands.Cog):
    """Unpopular but useful commands."""
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="avatar", description="Shows a user's avatar.", aliases=["av"])
    async def avatar(self, ctx: commands.Context, user: discord.User = None):
        """Shows a user's avatar."""
        if user == None:
            user = ctx.author

        async with ctx.typing():
            owner = await self.bot.fetch_user(869061991141101608)
            if user.avatar.is_animated():
                url = user.avatar.url
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                color_thief = ColorThief(BytesIO(response.content))
                dominant_color = color_thief.get_color(quality=5)
                embed = discord.Embed(title=f"{user.name}'s avatar",
                                    color=discord.Color.from_rgb(*dominant_color))
                embed.set_image(url=user.avatar.url)
                embed.add_field(
                    name="Download Links",
                    value=
                    f"[JPG]({user.avatar.with_static_format('jpg')}) | [PNG]({user.avatar.with_static_format('png')}) | [GIF]({user.avatar.with_format('gif')})"
                )
                embed.set_footer(text=f"Made by {owner.display_name}", icon_url=owner.avatar.url)
                await ctx.send(embed=embed)
            else:
                url = user.avatar.url
                response = requests.get(url)
                img = Image.open(BytesIO(response.content))
                color_thief = ColorThief(BytesIO(response.content))
                dominant_color = color_thief.get_color(quality=5)
                embed = discord.Embed(title=f"{user.name}'s avatar",
                                    color=discord.Color.from_rgb(*dominant_color))
                embed.set_image(url=user.avatar.url)
                embed.add_field(
                    name="Download Links",
                    value=
                    f"[JPG]({user.avatar.with_static_format('jpg')}) | [PNG]({user.avatar.with_static_format('png')})"
                )
                embed.set_footer(text=f"Made by {owner.display_name}", icon_url=owner.avatar.url)
                await ctx.send(embed=embed)

    @commands.hybrid_command(name="ui", description="Shows useful information about a user.")
    @app_commands.describe(user="The user who's info you want.")
    async def ui(self, ctx, user: discord.Member = None):
        """Shows useful information about a user."""
        owner = await self.bot.fetch_user(869061991141101608)
        if user == None:
            user = ctx.author

        rlist = []

        for role in user.roles:
            if role.name != "@everyone":
                rlist.append(role.mention)
                rlist.reverse()
        b = ", ".join(rlist)
        em = discord.Embed(
            timestamp=datetime.now(),
            color=user.top_role.color
        )
        stat = user.status
        date = user.created_at.strftime("%d/%m/%Y %H:%M")
        join = user.joined_at.strftime("%d/%m/%Y %H:%M")
        em.add_field(
            name="General Information",
            value=f"Username: {user.name}#{user.discriminator}\nUser ID: {user.id}\nStatus: {stat.name.title()}\nAvatar: [Click Here]({user.avatar.url})\nDate Created: {date}",
            inline=False
        )
        em.add_field(
            name="Server-Specific Information",
            value=f"Server Join Date: {join}\nTop Role: {user.top_role.mention}\nRoles ({len(rlist)}): {b}"
        )
        em.set_thumbnail(url=f"{user.avatar.url}")
        em.set_author(name=f"{user.display_name}'s User Info", icon_url=f"{user.avatar.url}")
        em.set_footer(text=f"Requested by {ctx.author.name} | Made by {owner.display_name}")

        await ctx.send(embed=em)

    @commands.hybrid_command(name="ping", description="Shows the bot's latency.")
    async def ping(self, ctx):
        """Shows the bot's latency."""
        start_time = time.monotonic()
        msg = await ctx.send("Pinging...")
        end_time = time.monotonic()
        latency = round((end_time - start_time) * 1000)
        await msg.edit(content=f"Pong! Latency: {latency}ms")
        

    
    def is_owner(interaction: discord.Interaction):
        if interaction.user.id == 869061991141101608:
            return True
        else:
            return False
        

    @app_commands.command(name="activity")
    @app_commands.check(is_owner)
    @app_commands.describe(activity="Type of activity.", name="Name of the activity.")
    @app_commands.choices(
        activity=[
            discord.app_commands.Choice(
                name="Playing",
                value=1
            ),
            discord.app_commands.Choice(
                name="Listening to",
                value=2
            ),
            discord.app_commands.Choice(
                name="Competing in",
                value=3
            ),
            discord.app_commands.Choice(
                name="Watching",
                value=4
            ),
            discord.app_commands.Choice(
                name="Streaming",
                value=5
            )
        ]
    )
    async def activity(self, interaction, activity: discord.app_commands.Choice[int], name:str):
        if activity.value == 1:
            await self.bot.change_presence(
                activity=discord.Game(name=f"{name}")
            )
        elif activity.value == 2:
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.listening, name=f"{name}")
            )
        elif activity.value == 3:
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.competing, name=f"{name}")
            )
        elif activity.value == 4:
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.watching, name=f"{name}")
            )
        elif activity.value == 5:
            await self.bot.change_presence(
                activity=discord.Activity(type=discord.ActivityType.streaming, name=f"{name}",
                 url="https://www.twitch.tv/kokohaan"
                 )
            )
        await interaction.response.send_message(f"Changed activity to `{activity.name} {name}`!", ephemeral=True)
    
    @commands.hybrid_command(name="echo", description="Send a message in a channel anonymously.", hidden=True)
    @commands.has_permissions(manage_messages=True)
    @app_commands.describe(channel="Where you want to send the message.", message="What you want to send.")
    async def echo(self, ctx, message: str, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel
        await channel.send(message)
        await ctx.reply("Sent!", ephemeral=True)


    @app_commands.command(name="announce", description="Announce something.")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.describe(
        channel="Where should I announce the message?",
        message="Text Message sent with the Embed",
        title="Embed Title",
        description="Embed Description",
        footer_text="Footer Text",
        timestamp="Current Timestamp",
        color="Embed Color hex code (#2F3136)",
        image="Image at the right corner. (url)"
    )
    @app_commands.choices(timestamp=[
        discord.app_commands.Choice(name="Yes", value=1),
        discord.app_commands.Choice(name="No", value=2)
    ])
    async def announce(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        title: str,
        description: str,
        footer_text: str,
        timestamp: discord.app_commands.Choice[int],
        message: str = None,
        color: str = None,
        image: str = None
    ):
        em = discord.Embed(
            title=title,
            description=description,
            timestamp=datetime.now() if timestamp.value == 1 else None,
            color=discord.Color.from_rgb(47, 49, 54) if color is None else discord.Color.from_str(color)
        )
        em.set_footer(text=footer_text)
        if image:
            em.set_image(url=f"{image}")
        await interaction.response.send_message(embed=em, content=f"Would you like to send this to {channel.mention}?", view=view, ephemeral=True)
        view = Confirm()
        await view.wait()
        if view.value is None:
            print('Timed out')
        elif view.value:
            await interaction.followup.send("Sent!")
            await channel.send(embed=em, content=message)
        else:
            await interaction.followup.send("Cancelled!")

    


async def setup(bot):
    await bot.add_cog(Miscellaneous(bot))
