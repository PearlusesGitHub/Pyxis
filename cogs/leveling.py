import json
import discord
from discord import app_commands
from discord.ext import commands
import random

async def open_account(user):
    users = await get_bank_data()

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

async def update_data(users, user):
    if not f'{user.id}' in users:
        users[f'{user.id}'] = {}
        users[f'{user.id}']['experience'] = 0
        users[f'{user.id}']['level'] = 1


async def add_experience(users, user, exp):
    users[f'{user.id}']['experience'] += exp


async def level_up(users, user, message):
    experience = users[f'{user.id}']['experience']
    lvl_start = users[f'{user.id}']['level']
    lvl_end = int(experience ** (1 / 4))
    if lvl_start < lvl_end:
        coins = int(lvl_end*4)
        await message.channel.send(
            f"🎊 **LEVEL UP**! {message.author.mention}, you are now level {lvl_end}. Enjoy these **{str(coins)} coins** as a thank you for your chat activity! 🎊")
        users[f'{user.id}']['level'] = lvl_end
        await update_bank_data(message.author, coins)

class Leveling(commands.Cog):
    """Gain exp and rank up!"""
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open('users.json', 'r') as f:
            users = json.load(f)

        await update_data(users, member)

        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)


    @commands.Cog.listener()
    async def on_message(self, message):
        with open('users.json', 'r') as f:
            users = json.load(f)
        await update_data(users, message.author)
        if not message.author.bot:
            with open('users.json', 'r') as f:
                users = json.load(f)

            await update_data(users, message.author)
            await add_experience(users, message.author, 2)
            await level_up(users, message.author, message)

            with open('users.json', 'w') as f:
                json.dump(users, f, indent=4)

    @commands.hybrid_command(name="rank", aliases=['level', 'exp', 'experience'], description="Shows a user's rank.")
    async def rank(self, ctx, member: discord.Member = None):
        """Shows a user's rank."""
        owner = await self.bot.fetch_user(869061991141101608)
        if member is None:
            member=ctx.author
        with open('users.json', 'r') as f:
            users = json.load(f)
        leader_board = {}
        total = []
        for user in users:
            name = int(user)
            exp = users[user]["experience"]
            leader_board[exp] = name
            total.append(exp)
        total = sorted(total, reverse=True)
        
        def get_position(key):
            sorted_leader_board = sorted(leader_board.items(), key=lambda x: x[0], reverse=True)
            for i, (_, value) in enumerate(sorted_leader_board, 1):
                if value == int(key):
                    return i
                
        pos = get_position(key=str(member.id))
        lvl = users[str(member.id)]['level']
        experience = users[str(member.id)]['experience']

        def ordinal(n: int):
            if 11 <= (n % 100) <= 13:
                suffix = 'th'
            else:
                suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
            return str(n) + suffix

        em = discord.Embed(
            title=f"{member.display_name}'s rank",
            color=discord.Color.random(),
            timestamp=ctx.message.created_at
        )
        em.set_footer(text=f"Made by {owner.display_name}", icon_url=f'{owner.avatar.url}')
        em.set_author(name=f"{member.display_name}", icon_url=member.avatar.url)
        em.add_field(name="Level", value=f"{lvl}", inline=False)
        em.add_field(name="Experience", value=f"{experience}", inline=False)
        em.add_field(name="Rank", value=f"{ordinal(n=pos)} out of {len(leader_board)} users", inline=False)
        await ctx.send(embed=em)





    @commands.hybrid_command(name="expleaderboard", aliases=['explb', 'xplb'], description="Displays the server experience leaderboard.")
    async def expleaderboard(self, ctx, x=10):
        """Displays the server experience leaderboard."""
        with open('users.json', 'r') as f:
            users = json.load(f)
        leader_board = {}
        total = []
        for user in users:
            name = int(user)
            exp = users[user]["experience"]
            leader_board[exp] = name
            total.append(exp)
        total = sorted(total, reverse=True)
        em = discord.Embed(
            title=f"Top {x} Active People",
            description="Following members are on the top of the leaderboard",
            color=discord.Color.random())
        owner = await self.bot.fetch_user(869061991141101608)
        em.set_footer(text=f"Made by {owner.display_name}", icon_url=owner.avatar.url)
        await ctx.defer(ephemeral=True)
        m = await ctx.send(embed=em)
        index = 1
        for exp in total:
            id_ = leader_board[exp]
            member = await self.bot.fetch_user(id_)
            name = member.display_name
            em.add_field(name=f"{index}. {name}", value=f"{exp}", inline=False)
            await m.edit(embed=em)
            if index == x:
                break
            else:
                index += 1


async def setup(bot):
    await bot.add_cog(Leveling(bot))
