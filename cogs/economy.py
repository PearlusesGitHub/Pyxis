import asyncio
import datetime
import json
import random
import typing
from datetime import datetime, time

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import Button
from discord.ext.commands.cooldowns import BucketType

def ordinal(n: int):
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        else:
            suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        return str(n) + suffix

async def open_account(user):
    users = await get_bank_data()

    with open('padlock.json', 'r') as f:
        padlockers = json.load(f)
    
    if str(user.id) in padlockers:
        return False
    else:
        padlockers[str(user.id)] = {}
        padlockers[str(user.id)]["Padlock"] = False
    
    with open("padlock.json", 'w') as f:
        json.dump(padlockers, f, indent=4)

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["Coins"] = 0

    with open("bank.json", 'w') as f:
        json.dump(users, f)

    return True


async def update_bank_data(user: discord.User, coins: int):
    await open_account(user=user)
    users = await get_bank_data()
    users[str(user.id)]["Coins"] += coins
    with open("bank.json", 'w') as f:
        json.dump(users, f, indent=4)


async def get_bank_data():
    with open("bank.json", 'r') as f:
        users = json.load(f)
    return users


class Economy(commands.Cog):
    """Earn, use, and gamble your virtual coins!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="balance", aliases=['bal', 'wallet'], description="Get a user's balance.")
    @app_commands.describe(user="The user who's balance you want to view.")
    async def balance(self, ctx, user: discord.Member = None):
        """Get a user\'s balance."""
        if user == None:
            user = ctx.author

        await open_account(user)
        users = await get_bank_data()
        bal = users[str(user.id)]["Coins"]
        with open('padlock.json', 'r') as f:
            padlockers = json.load(f)
        em = discord.Embed(
            title=f"{user.name}#{user.discriminator}'s balance",
            description=f":moneybag: {user.mention} has **{str(bal)} coins**!",
            color=discord.Colour.random(),
            timestamp=datetime.now()
        )
        em.add_field(name="Padlock", value=str(padlockers[str(user.id)]["Padlock"]))
        em.set_author(name=f"{user.name}", icon_url=f"{user.avatar.url}")
        await ctx.send(embed=em)
    
    @commands.hybrid_command(name="work", description="Work for 20-50 coins.")
    @commands.cooldown(1, 60*30, commands.BucketType.user)
    async def work(self, ctx):
        """Work for 20-50 coins."""
        await open_account(user=ctx.author)
        coins = random.randint(20, 50)
        em = discord.Embed(
            description=f"You work for half an hour and earn **{coins} coins**!",
            color=discord.Colour.green()
        )
        em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                      icon_url=f"{ctx.author.avatar.url}")
        await ctx.send(embed=em)
        await update_bank_data(ctx.author, coins)

    @commands.hybrid_command(name="daily", description="Collect your daily coins. [50-75]")
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """Collect your daily coins. [50-75]"""
        await open_account(user=ctx.author)
        coins = random.randint(50, 75)
        em = discord.Embed(
            color=discord.Color.green(),
            description=f"Collected daily income! You got **{coins} coins**."
        )
        em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                      icon_url=f"{ctx.author.avatar.url}")
        await ctx.send(embed=em)
        await update_bank_data(ctx.author, coins)
 
    @daily.error
    async def daily_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = int(error.retry_after)
            hours, minutes = divmod(int(remaining_time), 3600)
            em = discord.Embed(
                description=
                f"You've already collected today's daily income, try again in {hours} hours and {round(minutes / 60)} minutes.",
                color=discord.Color.from_rgb(212, 0, 0))
            em.set_author(name=f"{ctx.author.name}",
                          icon_url=f'{ctx.author.avatar.url}#{ctx.author.discriminator}')
            await ctx.defer(ephemeral=True)
            await ctx.send(embed=em)

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = int(error.retry_after)
            minutes, seconds = divmod(int(remaining_time), 60)
            em = discord.Embed(
                description=
                f"Quit working so hard. You can work again in {minutes} minutes and {seconds} seconds.",
                color=discord.Color.from_rgb(212, 0, 0))
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                          icon_url=f'{ctx.author.avatar.url}')
            await ctx.defer(ephemeral=True)
            await ctx.send(embed=em)

    @commands.hybrid_command(name="crime", description="Go on a crime spree to get or lose coins. [-50, 50]")
    @commands.cooldown(1, 15*60, commands.BucketType.user)
    async def crime(self, ctx):
        """Go on a crime spree to get or lose coins. [-50, 50]"""
        await open_account(ctx.author)
        users = await get_bank_data()
        coins = random.randint(-50, 50)
        if coins > 0:
            em = discord.Embed(
                description=f"You go on a crime spree and get **{str(coins)} coins**.",
                timestamp=datetime.now(),
                color=discord.Color.green()
            )
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}", icon_url=f"{ctx.author.avatar.url}")
            await ctx.send(embed=em)
            await update_bank_data(ctx.author, coins)
        elif coins < 0:
            em = discord.Embed(
                description=f"You go on a crime spree and get caught. " \
                            f"Your bail costs you **{str(coins)} coins**.",
                timestamp=datetime.now(),
                color=discord.Color.from_rgb(212, 0, 0)
            )
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                          icon_url=f'{ctx.author.avatar.url}')
            await ctx.send(embed=em)
            await update_bank_data(ctx.author, coins)

    @crime.error
    async def crime_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = int(error.retry_after)
            minutes, seconds = divmod(int(remaining_time), 60)
            em = discord.Embed(
                description=
                f"If you keep committing crimes, you can get caught! " \
                f"You can commit a crime again in {minutes} minutes and {seconds} seconds.",
                color=discord.Color.from_rgb(212, 0, 0))
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                          icon_url=f'{ctx.author.avatar.url}')
            await ctx.defer(ephemeral=True)
            await ctx.send(embed=em)
    
    @commands.hybrid_command(name="flip", description="Flip a coin to earn or lose coins.")
    @app_commands.describe(side="Heads or Tails.", bet="Amount of coins to bet.")
    @commands.cooldown(1, 60 * 2, commands.BucketType.user)
    async def flip(self, ctx, side: str, bet: int):
        """Flip a coin to earn or lose coins."""
        await open_account(user=ctx.author)
        users = await get_bank_data()
        bal = users[str(ctx.author.id)]["Coins"]
        
        if side == "h":
            side = "heads"
        elif side == "t":
            side = "tails"

        if side.lower() not in ["heads", "tails"]:
            em = discord.Embed(
                title="Not a valid side",
                description="Choose either `heads` or `tails`.",
                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.reset_cooldown(ctx)
            await ctx.send(embed=em)
            return

        if bet is None or bet < 100:
            em = discord.Embed(
                title="Invalid Bet",
                description="Please bet more than 100 coins.",
                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.reset_cooldown(ctx)
            await ctx.send(embed=em)
            return

        if bal < bet:
            em = discord.Embed(
                title="Not Enough Coins",
                description="You don't have enough coins to make that bet.",
                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.send(embed=em)
            return

        result = random.choice(["heads", "tails"])
        won_or_lost = -bet if result != side.lower() else bet
        em = discord.Embed(
            title=f"{ctx.author.name} flips a coin",
            description="The coin is spinning in the air",
            color=discord.Color.from_rgb(255, 255, 255))
        em.set_author(
            name=f"{ctx.author.name}#{ctx.author.discriminator}",
            icon_url=f"{ctx.author.avatar.url}")
        msg = await ctx.send(embed=em)
        await asyncio.sleep(1)
        em1 = discord.Embed(
            title=f"{ctx.author.name} flipped the coin",
            description=f"It landed on {result}, you {'' if won_or_lost > 0 else 'lost 💰'}{abs(won_or_lost)} coins.",
            color=discord.Colour.green() if won_or_lost > 0 else discord.Color.from_rgb(212, 0, 0))
        em1.set_author(
            name=f"{ctx.author.name}#{ctx.author.discriminator}",
            icon_url=f"{ctx.author.avatar.url}")
        await update_bank_data(user=ctx.author, coins=int(won_or_lost))
        await msg.edit(embed=em1)


    @flip.error
    async def flip_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = int(error.retry_after)
            minutes, seconds = divmod(int(remaining_time), 60)
            em = discord.Embed(
                title="Command on cooldown",
                description=
                f"Slow down and try again in {minutes} minutes and  {seconds} seconds.",
                color=discord.Color.from_rgb(212, 0, 0))
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                            icon_url=f'{ctx.author.avatar.url}')
            await ctx.send(embed=em)

    @commands.hybrid_command(name="dice", aliases=['die', 'roll'], description="Roll a die to win or lose coins.")
    @app_commands.describe(side="1, 2, 3, 4, 5, 6", bet="Amount of coins to bet")
    async def dice(self, ctx, side: str, bet: int):
        """Roll a die to win or lose coins."""
        channels = [903968715727581184]
        if ctx.channel.id not in channels:
            return

        if side is None or bet is None:
            em = discord.Embed(
                title="Dice Command",
                description="Bet coins on a dice. `,dice {side} [coins]`",
                color=discord.Color.dark_gold())
            await ctx.defer(ephemeral=True)
            return await ctx.send(embed=em)

        await open_account(user=ctx.author)
        users = await get_bank_data()
        bal = users[str(ctx.author.id)]["Coins"]
        dicesides = ["1", "2", "3", "4", "5", "6"]
        if bet < 100 or bal < bet or side not in dicesides:
            if bet < 100:
                description = "Please bet more than 💰 100 coins."
            elif bal < bet:
                description = "You don't have that many coins."
            else:
                description = "Choose either `1`, `2`, `3`, `4`, `5`, `6`."
            em = discord.Embed(
                title="Invalid input",
                description=description,
                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.defer(ephemeral=True)
            return await ctx.send(embed=em)

        result = random.choice(dicesides)
        if result == side:
            em_color = discord.Colour.green()
            em_description = f"It landed on {result}, you won 💰 **{bet} coins**."
            await update_bank_data(user=ctx.author, coins=int(bet))
        else:
            em_color = discord.Color.from_rgb(212, 0, 0)
            em_description = f"It landed on {result}, you lost 💰 **{bet} coins**."
            await update_bank_data(user=ctx.author, coins=int(-bet))

        em = discord.Embed(
            title=f"{ctx.author.name} rolls a dice",
            description=f"The dice is rolling.",
            color=discord.Color.from_rgb(255, 255, 255))
        em.set_author(
            name=f"{ctx.author.name}#{ctx.author.discriminator}",
            icon_url=f'{ctx.author.avatar.url}')
        msg = await ctx.send(embed=em)
        await asyncio.sleep(1)
        em1 = discord.Embed(
            title=f"{ctx.author.name} rolled a dice",
            description=em_description,
            color=em_color)
        em1.set_author(
            name=f"{ctx.author.name}#{ctx.author.discriminator}",
            icon_url=f'{ctx.author.avatar.url}')
        return await msg.edit(embed=em1)

    
    @commands.hybrid_command(name="change", description="Change a user's coins.", hidden=True)
    @commands.has_permissions(administrator=True)
    @app_commands.describe(
        user="User who's coins to change.",
        coins="What to change the coins to."
    )
    async def change(self, ctx, user: discord.Member, coins: int):
        await open_account(user)
        if coins < 0:
            await ctx.defer(ephemeral=True)
            return await ctx.reply("Coins can't be negative!")

        users = await get_bank_data()
        old_bal = users[str(user.id)]["Coins"]
        users[str(user.id)]["Coins"] = coins
        with open("bank.json", 'w') as f:
            json.dump(users, f, indent=4)

        em = discord.Embed(
            title="Coins changed",
            description=f"Coins changed for {user.mention}.",
            colour=discord.Color.gold(),
            timestamp=datetime.now()
        )
        em.add_field(
            name="Old Balance",
            value=f":moneybag: **{old_bal} coins**",
            inline=False
        )
        em.add_field(
            name="New Balance",
            value=f":moneybag: **{coins} coins**",
            inline=False
        )
        em.add_field(
            name="Admin",
            value=f"{ctx.author.mention}",
            inline=False
        )

        log_channel = await self.bot.fetch_channel(955026384105897984)
        await ctx.defer(ephemeral=True)
        await ctx.reply(embed=em)
        await log_channel.send(embed=em)

    
    @commands.hybrid_command(name="gift", description="Gift your coins to someone.")
    @app_commands.describe(
        user="User who you want to gift your coins.",
        coins="Amount of coins you want to gift.",
        note="Message to leave to the user."
    )
    async def gift(self, ctx, user: discord.Member, coins: int, note: str):
        """Gift your coins to someone."""
        await open_account(user)
        await open_account(ctx.author)
        if user is None:
            em = discord.Embed(
                title="No user tagged",
                description=
                "Please mention the user you want to transfer your money to.",
                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.send(embed=em)
        if coins is None:
            em = discord.Embed(
                title="No amount entered",
                description="Please enter the amount of coins you want to transfer.",
                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.send(embed=em)
        coins = int(coins)
        users = await get_bank_data()
        bal = users[str(ctx.author.id)]["Coins"]
        if user == ctx.author:
            em = discord.Embed(title="Can't gift yourself",
                                description="You can't gift yourself.",
                                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.send(embed=em)
        elif coins < 0:
            em = discord.Embed(title="Invalid amount",
                                description="Amount must be positive.",
                                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.send(embed=em)
        elif bal < coins:
            em = discord.Embed(title="Not enough coins",
                                description="You don't have enough coins.",
                                color=discord.Color.from_rgb(212, 0, 0))
            await ctx.send(embed=em)
        else:
            await update_bank_data(user, coins)
            em = discord.Embed(
                title="Coins Sent",
                description=
                f"You've successfully sent 💰 {coins} coins to {user.mention}.",
                color=discord.Color.green())
            await ctx.send(embed=em)
            em = discord.Embed(
                title="Coins Received",
                description=f"{ctx.author.mention} just gifted you 💰 {coins} coins! \nNote: `{note}`",
                color=discord.Color.gold())
            await user.send(embed=em)
            await update_bank_data(ctx.author, -coins)
        
    @commands.hybrid_command(name="beg", description="Beg for some coins.")
    @commands.cooldown(1, 60*10, commands.BucketType.user)
    async def beg(self, ctx):
        """Beg for some coins."""
        await open_account(ctx.author)
        users = await get_bank_data()
        bal = users[str(ctx.author.id)]["Coins"]
        if bal > 1000:
            coins = random.randint(50, 75)
            em = discord.Embed(
                description=f"You beg on the streets in shabby clothes and get **{str(coins)} coins**.",
                timestamp=datetime.now(),
                color=discord.Color.green()
            )
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                        icon_url=f"{ctx.author.avatar.url}")
            await update_bank_data(ctx.author, coins)
            await ctx.send(embed=em)
        elif bal < 1000:
            coins = random.randint(10, 30)
            em = discord.Embed(
                description=f"You beg on the streets and get **{str(coins)} coins**.",
                timestamp=datetime.now(),
                color=discord.Color.green()
            )
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                        icon_url=f"{ctx.author.avatar.url}")
            await update_bank_data(ctx.author, coins)
            await ctx.send(embed=em)

    @beg.error
    async def beg_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = int(error.retry_after)
            minutes, seconds = divmod(int(remaining_time), 60)
            em = discord.Embed(
                description=
                f"You can't beg for long or you'll get caught. "
                f"You can work again in {minutes} minutes and {seconds} seconds.",
                color=discord.Color.from_rgb(212, 0, 0))
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                          icon_url=f'{ctx.author.avatar.url}')
            await ctx.defer(ephemeral=True)
            await ctx.send(embed=em)

    @commands.hybrid_command(name="rob", description="Rob a user anonymously if they don't have a padlock. [+100 if you succeed, else -30]")
    @app_commands.describe(user="Who you want to rob.")
    @commands.cooldown(1, 60*5, commands.BucketType.user)
    async def rob(self, ctx, user: discord.Member):
        """Rob a user anonymously if they don't have a padlock."""
        await open_account(ctx.author)
        await open_account(user)
        users = await get_bank_data()
        bal = users[str(ctx.author.id)]["Coins"]
        bal1 = users[str(user.id)]["Coins"]
        with open('padlock.json', 'r') as f:
            padlockers = json.load(f)
        await ctx.message.delete()
        if not user:
            await ctx.reset_cooldown(ctx)
            await ctx.send("No user mentioned!")
        
        if not padlockers[str(user.id)]["Padlock"]:
            if bal < 100:
                await ctx.defer(ephemeral=True)
                await ctx.reply("You need to have atleast 100 coins to rob someone.")
                await ctx.reset_cooldown(ctx)
            elif bal1 < 100:
                await ctx.defer(ephemeral=True)
                await ctx.reply("The user you want to rob doesn't have that many coins.")
                await ctx.reset_cooldown(ctx)
            choice = [True, True, True, False, False, False, False, False, False, False]
            if random.choice(choice):
                await update_bank_data(user, -100)
                await update_bank_data(ctx.author, 100)
                m = await ctx.reply(f"Attempting to rob **{user.name}#{user.discriminator}**...")
                await asyncio.sleep(2)
                await m.edit(f"Rob successful! You got **100 coins**!")
            else:
                await update_bank_data(user, 30)
                await update_bank_data(ctx.author, -30)
                m = await ctx.reply(f"Attempting to rob **{user.name}#{user.discriminator}**")
                await asyncio.sleep(2)
                await m.edit(f"Rob failed! You lost **30 coins**!")
        elif padlockers[str(user.id)]["Padlock"]:
            await ctx.send(f"Rob failed! **{user.name}#{user.discriminator}** has a padlock.")

    @rob.error
    async def rob_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            remaining_time = int(error.retry_after)
            minutes, seconds = divmod(int(remaining_time), 60)
            em = discord.Embed(
                description=
                f"You can't rob again or the FBI will catch you!"
                f"You can rob again in {minutes} minutes and {seconds} seconds.",
                color=discord.Color.from_rgb(212, 0, 0))
            em.set_author(name=f"{ctx.author.name}#{ctx.author.discriminator}",
                          icon_url=f'{ctx.author.avatar.url}')
            await ctx.defer(ephemeral=True)
            await ctx.send(embed=em)

    @commands.hybrid_command(name='shop', description="Displays the server shop.")
    async def shop(self, ctx):
        """Displays the server shop."""
        owner = await self.bot.fetch_user(869061991141101608)
        with open("role.json", 'r') as f:
            h = json.load(f)
        r = h["role_id"]
        role = discord.utils.get(ctx.guild.roles, id=int(r))
        em = discord.Embed(
            title=f"{ctx.guild.name} Shop",
            description=f"**{role.mention} role**\nPrice: 💰 1000 coins | ID: `1`",
            color=discord.Color.random(),
            timestamp=datetime.now()
        )
        em.add_field(name="Padlock", value="Price: 💰 1500 coins | ID: `2`")
        em.add_field(name="Custom Role", value="Price: 💰  5000 coins | ID: `3`", inline=False)
        em.add_field(name="Role Icon", value="Price: 💰 3000 coins | ID: `4`", inline=False)
        em.add_field(name="Nickname Permissions", value="Price: 💰 10000 coins | ID: `5`", inline=False)
        em.set_footer(text=f"Made by {owner.display_name}#{owner.discriminator}", icon_url=f"{owner.avatar.url}")
        await ctx.defer(ephemeral=True)
        await ctx.send(embed=em)
    
    from typing import Literal
    
    @app_commands.command(name="changerole", description="Change the monthly role.")
    async def changerole(self, interaction: discord.Interaction, role: discord.Role):
        if interaction.user.id == 869061991141101608:
            with open("role.json", 'r') as f:
                h = json.load(f)
            r = h["role_id"]
            await interaction.response.send_message(content=f"Changed role to {role.mention}! Old role: <@&{r}>.")
            h["role_id"] = role.id
            with open("role.json", 'w') as f:
                json.dump(h, f, indent=4)
            
        else:
            await interaction.response.send_message("You aren't cool enough to use this command!")
               

    @commands.hybrid_command(name='buy', description="Buy an item from the shop. [,shop]")
    @app_commands.describe(item="The item you want to buy.")
    async def buy(self, ctx, item: str):
        """Buy an item from the shop. [,shop]"""
        if item is None:
            await ctx.reply("Specify an item ID! See `,shop`")

        users = await get_bank_data()
        bal = users[str(ctx.author.id)]["Coins"]

        with open("role.json", 'r') as f:
            h = json.load(f)
        r = h["role_id"]
        monthly = discord.utils.get(ctx.guild.roles, id=int(r))

        if item == "1":
            if monthly in ctx.author.roles:
                await ctx.defer(ephemeral=True)
                return await ctx.send(f"{ctx.author.mention}, you already have that item. Go buy something new!")
            if bal >= 1000:
                await ctx.send(
                    f"{ctx.author.mention}, you've successfully purchased **{monthly.name}** role!")
                
                
                await update_bank_data(user=ctx.author, coins=-1000)
                await ctx.author.add_roles(monthly)
            elif bal < 1000:
                await ctx.defer(ephemeral=True)
                return await ctx.send(f"{ctx.author.mention}, you don't have enough coins to buy that item.")
            return

        elif item == "3":
            if bal >= 5000:
                await ctx.send(
                    f"{ctx.author.mention}, you've successfully purchased **Custom Role**! A moderator will fulfill your order soon!")
                
                await update_bank_data(user=ctx.author, coins=-5000)
                channel = self.bot.get_channel(927440324056453150)
                em = discord.Embed(
                    title="Custom role purchased",
                    description=f"{ctx.author.mention} has bought a custom role.",
                    color=discord.Color.random(),
                    timestamp=datetime.datetime.utcnow()
                )
                await channel.send("<@&927987250904563796>")
                return await channel.send(embed=em)
            elif bal < 5000:
                await ctx.defer(ephemeral=True)
                return await ctx.send(f"{ctx.author.mention}, you don't have enough coins to buy that item.")
            return
        
        elif item == "2":
            if bal >= 1500:
                await ctx.send(
                    f"{ctx.author.mention}, you've successfully purchased **Padlock**! You are now protected from robbers."
                )
                with open('padlock.json', 'r') as f:
                    padlockers = json.load(f)
                if padlockers[str(ctx.author.id)]["Padlock"] == True:
                    await ctx.send("You've already purchased this item. Go buy something new!")
                elif ctx.author.id not in padlockers:
                    padlockers[str(ctx.author.id)] = {}
                    padlockers[str(ctx.author.id)]["Padlock"] = True
                    with open('padlock.json', 'w') as f:
                        padlockers = json.dump(padlockers, f, indent=4)
                    await update_bank_data(ctx.author, -1500)

        
        elif item == "4":
            if bal >= 4000:
                await ctx.send(
                    f"{ctx.author.mention}, you've successfully purchased **Role Icon**! A moderator will fulfill your order soon!")
                await update_bank_data(user=ctx.author, coins=-4000)
                channel = self.get_channel(927440324056453150)
                em = discord.Embed(
                    title="Role icon purchased",
                    description=f"{ctx.author.mention} has bought a role icon.",
                    color=discord.Color.random(),
                    timestamp=datetime.datetime.utcnow()
                )
                return await channel.send(embed=em)
            elif bal < 4000:
                await ctx.defer(ephemeral=True)
                return await ctx.send(f"{ctx.author.mention}, you don't have enough coins to buy that item.")
            
        elif item == "5":
            custom = discord.utils.get(ctx.guild.roles, id=929296476100788305)
            if custom in ctx.author.roles:
                return await ctx.send(f"{ctx.author.mention}, you already have that item. Go buy something new!")
            if bal >= 10000:
                await ctx.send(f"{ctx.author.mention}, you've successfully purchased **Nickname Permissions**!")
                await ctx.author.add_roles(custom)
                await update_bank_data(user=ctx.author, coins=-10000)
                return
            elif bal < 10000:
                await ctx.defer(ephemeral=True)
                return await ctx.send(f"{ctx.author.mention}, you don't have enough coins to buy that item.")
            return
        
        else:
            await ctx.defer(ephemeral=True)
            return await ctx.send(f"{ctx.author.mention}, no such item exists, please choose an item from the shop!")

    @commands.hybrid_command(name="leaderboard", aliases=['lb'], description="Displays the server economy leaderboard")
    @app_commands.describe(num="Number of users to display on the leaderboard.")
    async def leaderboard(self, ctx, num: int = 10):
        """Displays the server economy leaderboard"""
        owner = await self.bot.fetch_user(869061991141101608)
        users = await get_bank_data()
        leader_board = {coins: int(user) for user, data in users.items() for coins in (data["Coins"],)}
        total = sorted(list(set(leader_board.keys())), reverse=True)

        em = discord.Embed(
            title=f"Top {num} Richest People",
            description="Following members are on the top of the leaderboard.",
            color=discord.Color.gold())

        await ctx.defer(ephemeral=True)
        m = await ctx.reply(embed=em, mention_author=False)
        em.set_footer(text=f"Made by {owner.display_name}#{owner.discriminator}", icon_url=owner.avatar.url)

        for index, coins in enumerate(total[:num], start=1):
            id_ = leader_board[coins]
            member = await self.bot.fetch_user(id_)
            name = member.display_name
            em.add_field(name=f"{index}. {name}", value=f"{coins}", inline=False)
            await m.edit(embed=em)

    @commands.hybrid_command(name="slots", description="Bet your coins on a game of slots.")
    @app_commands.describe(bet="Amount of coins to bet.")
    async def slots(self, ctx, bet: int):
        """Bet your coins on a game of slots."""
        list = [":yellow_circle:", ":red_circle:", ":green_circle:"]
        outcome1 = random.choice(list)
        outcome2 = random.choice(list)
        outcome3 = random.choice(list)
        await update_bank_data(ctx.author, -bet)
        if bet == None:
            em = discord.Embed(
                title="No coins bet",
                description="Please bet atleast 100 coins for slots.",
                color=discord.Color.dark_red()
            )
            return await ctx.send(embed=em)
        elif bet < 100:
            em = discord.Embed(
                title="Too less of a bet",
                description="Please bet atleast 100 coins for slots.",
                color=discord.Color.dark_red()
            )
            return await ctx.send(embed=em)
        users = await get_bank_data()
        bal = users[str(ctx.author.id)]["Coins"]
        if bal < bet:
            em = discord.Embed(
                title="Not enough coins",
                description=f"You do not have that much coins. You need more {int(bet) - bal} coins.",
                color=discord.Color.dark_red()
            )
            return await ctx.send(embed=em)

        if outcome1 == outcome2 == outcome3:
            em = discord.Embed(
                title="Slots are spinning",
                description=":white_circle: :white_circle: :white_circle:",
                color=discord.Color.light_grey()
            )
            m = await ctx.send(embed=em)
            await asyncio.sleep(2)
            em1 = discord.Embed(
                title="Slots result",
                description=f"{outcome1} {outcome2} {outcome3}",
                color=discord.Color.green()
            )
            await m.edit(embed=em1)
            await ctx.channel.send(f"You've won **{str(bet)} coins**!")
            await update_bank_data(user=ctx.author, coins=bet)
            return
        elif outcome1 != outcome2 != outcome3:
            em = discord.Embed(
                title="Slots are spinning",
                description=":white_circle: :white_circle: :white_circle:",
                color=discord.Color.light_grey()
            )
            m = await ctx.send(embed=em)
            await asyncio.sleep(2)
            em1 = discord.Embed(
                title="Slots result",
                description=f"{outcome1} {outcome2} {outcome3}",
                color=discord.Color.from_rgb(255, 0, 0)
            )
            await m.edit(embed=em1)
            await ctx.channel.send(f"You lost **{str(bet)} coins**.")
            await update_bank_data(user=ctx.author, coins=-bet)
            return
        elif outcome1 == outcome2 != outcome3:
            em = discord.Embed(
                title="Slots are spinning",
                description=":white_circle: :white_circle: :white_circle:",
                color=discord.Color.light_grey()
            )
            m = await ctx.send(embed=em)
            await asyncio.sleep(2)
            em1 = discord.Embed(
                title="Slots result",
                description=f"{outcome1} {outcome2} {outcome3}",
                color=discord.Color.from_rgb(255, 0, 0)
            )
            await m.edit(embed=em1)
            await ctx.channel.send(f"You lost **{str(bet)} coins**.")
            await update_bank_data(user=ctx.author, coins=-bet)
            return
        elif outcome1 != outcome2 == outcome3:
            em = discord.Embed(
                title="Slots are spinning",
                description=":white_circle: :white_circle: :white_circle:",
                color=discord.Color.light_grey()
            )
            m = await ctx.send(embed=em)
            await asyncio.sleep(2)
            em1 = discord.Embed(
                title="Slots result",
                description=f"{outcome1} {outcome2} {outcome3}",
                color=discord.Color.from_rgb(255, 0, 0)
            )
            await m.edit(embed=em1)
            await ctx.channel.send(f"You lost **{str(bet)} coins**.")
            await update_bank_data(user=ctx.author, coins=-bet)
            return

    @app_commands.command(name="scratch", description="Scratch lucky boxes and win prizes.")
    async def scratch(self, interaction: discord.Interaction):
        global ans
        modal= ScratchModal()
        
        users = await get_bank_data()
        balance = users[f'{interaction.user.id}']["Coins"]
        if balance < 200:
            return await interaction.followup.send(f"You need {150 - balance} more coins to buy a scratch ticket.")

        await update_bank_data(interaction.user, -150)

        empty = self.bot.get_emoji(982579283635617802)
        plus_hun = self.bot.get_emoji(982580517344018463)
        plus_five_hun = self.bot.get_emoji(982580519692812298)
        min_hun = self.bot.get_emoji(982580521978716220)
        min_two_hun = self.bot.get_emoji(982580524054880306)
        min_fif = self.bot.get_emoji(982580526252695622)

        emojis = {
            empty: "You won nothing.",
            plus_hun: "You won **100 coins**!",
            plus_five_hun: "You won **500 coins**!",
            min_hun: "You lost **100 coins**.",
            min_two_hun: "You lost **200 coins**.",
            min_fif: "You lost **50 coins**."
        }

        emojis_weights = [0.1, 0.5, 0.1, 0.1, 0.1, 0.1]
        cum_weights = [sum(emojis_weights[:i+1]) for i in range(len(emojis_weights))]
        cum_weights[-1] = 1.0

        emojis_list = random.choices(list(emojis.keys()), k=9, cum_weights=cum_weights)
        c1 = random.choice(emojis_list)
        c2 = random.choice(emojis_list)
        c3 = random.choice(emojis_list)
        c4 = random.choice(emojis_list)
        c5 = random.choice(emojis_list)
        c6 = random.choice(emojis_list)
        c7 = random.choice(emojis_list)
        c8 = random.choice(emojis_list)
        c9 = random.choice(emojis_list)
        board = f"{c1}{c2}{c3}\n{c4}{c5}{c6}\n{c7}{c8}{c9}"
        lucky = "<:luckyblock:982569561855496212>"
        await interaction.response.send_modal(modal)
        m = await interaction.followup.send(f"{lucky}{lucky}{lucky}\n{lucky}{lucky}{lucky}\n{lucky}{lucky}{lucky}", ephemeral=True)
        await modal.wait()
        
        if ans is None:
            await update_bank_data(interaction.user, 200)
            return await interaction.channel.send("Timed out! Coins refunded")
        if any([c1, c2, c3, c4, c5, c6, c7, c8, c9]) != list(emojis.keys())[0]:
            await m.edit(content=board)
            for i in range(1, 10):
                if ans == str(i):
                    result = eval("c" + str(i))
                    await interaction.channel.send(emojis.get(result))
                    val = emojis.get(result)
                    number = val.split()[2]
                    try:
                        coins = int(number[2:])
                    except ValueError:
                        coins = 0
                    await update_bank_data(interaction.user, coins=coins if 'won' in val else -coins)
        elif any([c1, c2, c3, c4, c5, c6, c7, c8, c9]) == list(emojis.keys())[0]:
            await m.edit(content=board)
            for i in range(1, 10):
                if ans == str(i):
                    result = eval("c" + str(i))
                    await interaction.channel.send(emojis.get(result))

ans = None
class ScratchModal(discord.ui.Modal,
 title="Enter the number of the box to scratch [1-9].",
 ):
    def __init__(self, *, title: str = "Enter the number of the box to scratch [1-9].", timeout: float = 30.0):
        super().__init__(title=title, timeout=timeout)

    num = discord.ui.TextInput(
        label="Input your choice.",
        style=discord.TextStyle.short,
        required=True,
        placeholder="1,2,3,4,5,6,7,8,9",
        min_length=1,
        max_length=1
    )
    async def on_submit(self, interaction: discord.Interaction):
        global ans
        ans = self.num.value
        await interaction.response.send_message("Submitting...")
    
    async def on_timeout(self, interaction: discord.Interaction):
        global ans
        ans = None
        await interaction.response.send_message("Timed out!")
        
async def setup(bot):
    await bot.add_cog(Economy(bot))
   