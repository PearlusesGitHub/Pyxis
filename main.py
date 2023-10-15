# Imports
import asyncio
import json
import os
import random
import datetime

import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands import command
from dotenv import load_dotenv
import time

os.system('python3 -m pip install -r requirements.txt')

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(
    command_prefix=commands.when_mentioned_or(','),
    help_command=None,
    activity=discord.Activity(
        type=discord.ActivityType.listening,
        name=",help"),
    intents=intents,
    strip_after_prefix=True,
    status=discord.Status.online,
    case_insensitive=True
)

@bot.event
async def on_message(message):
    if message.content == any(['<@955013929095016468>', '<@!955013929095016468>']):
        await message.channel.send(f"{message.author.mention}, my prefix is `,`! Use `,help` to see my commands.")
    
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Try using `,help` to see all commands!")
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Please pass in all required arguments.')
    if isinstance(error, commands.HybridCommandError):
        await ctx.send(f"```{error}```")
    
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
    

@bot.command(hidden=True)
async def syntaxes(ctx):
    em = discord.Embed(title="Command Syntaxes", color=discord.Color.random())
    em.set_footer(text="* is optional parameter.")
    em.add_field(name="**__Miscellaneous Commands__**",
                 value="List",
                 inline=False)
    em.add_field(name="**,ui**", value="`,ui {user}*`", inline=False)
    em.add_field(name="**,quote**", value="`,quote` / `,q`", inline=False)
    em.add_field(name="**,avatar**",
                 value="`,avatar {user}*` / `,av {user}*`",
                 inline=False)
    em.add_field(name="**,ping**", value="`,ping`", inline=False)
    em.add_field(name="**,remind**",
                 value="`,remind {time}s|m|h|d [task]`",
                 inline=False)
    em.add_field(name="**__Economy Commands__**", value="List", inline=False)
    em.add_field(name="**,balance**",
                 value="`,bal {user}`* / `,balance {user}`*",
                 inline=False)
    em.add_field(name="**,work**", value="`,work`", inline=False)
    em.add_field(name="**,crime**", value="`,crime`", inline=False)
    em.add_field(name="**,flip**",
                 value="`,flip heads/tails (coins)`",
                 inline=False)
    em.add_field(name="**,dice**",
                 value="`,dice 1/2/3/4/5/6 (coins)`",
                 inline=False)
    em.add_field(name="**,scratch**",
                 value="`,gift`",
                 inline=False)
    em.add_field(name="**,shop**", value="`,shop`", inline=False)
    em.add_field(name="**,leaderboard**",
                 value="`,leaderboard` / `,lb`",
                 inline=False)
    em.add_field(name="**,meme**",
                 value="`,meme`",
                 inline=False)
    em.add_field(name="**,place**",
                 value="`,place (box)`",
                 inline=False)
    em.set_author(name=f"{bot.user.name}", icon_url=bot.user.avatar.url)
    await ctx.send(embed=em)

@bot.command(hidden=True)
async def ecoinfo(ctx):
    if ctx.author.id == 869061991141101608:
        embed = discord.Embed(title="Server Economy~",
                              description=f"Welcome to the very own Economy of {ctx.guild.name}", color=0x98d7ff)
        embed.set_author(name=f"{ctx.guild.name}",
                         icon_url=f"{bot.user.avatar.url}")
        embed.set_thumbnail(
            url=f"{ctx.guild.avatar.url}")
        embed.add_field(name="How can I earn money?",
                        value="Following are some commands which can gain you some quick money. We will be referring to money as 'coins' from now on. \n`,work` : Gives you 1-50 coins with a cooldown of 30 minutes. \n`,crime` : Commit a crime to either get or lose coins with a 50-50 chance and a cooldown of 15 minutes. \n`,daily` : Collect your daily income of 50-75 coins. To view your balance, use the `,bal` command.",
                        inline=False)
        embed.add_field(name="How can I gamble money?",
                        value="The Bot consists of many gambling commands. Their use and syntaxes are shown in details in the `,help` command. Gambling commands include:\n`,flip` : Flip a coin e.g. `,flip heads 100`. \n`,dice` : Roll a die e.g. `,dice 5 100`. \n`,slots` : Bet your coins on a game of slots e.g. `,slots 100`. \n</scratch:1071772747329445958> : Scratch lucky boxes and win prizes.",
                        inline=False)
        embed.add_field(name="Other economy commands.",
                        value="Some more economy commands include `,leaderboard` or `,lb` which shows the richest people in the server on a leaderboard.",
                        inline=False)
        embed.add_field(name="Server Shop~",
                        value="The server has it's own shop which includes four items:\nMonthly Role:- Every month, you can stack up more unique roles.\nPadlock:- Protect yourself from robbery.\nCustom Role:- Get your own custom role. \nRole Icon:- A custom role icon to go with your role. Custom role needed.\nNickname Permissions:- Allows you to have a nickname for the server. \nThe prices can be viewed using the `,shop` command.",
                        inline=False)
        await ctx.channel.send(embed=embed)


# embeds for the questions
import random

import discord
from discord.ext import tasks

last_question_timestamp = None
current_question = None
m_id = None

dishes = ["coffee", "tea", "parfait", "orange mocktail", "donut", "croissant", "espresso", "latte"] # Customisable with your own words

def sel_question():
    random.shuffle(questions)
    question = random.choice(questions)
    return question

def sel_dish():
    dish = random.choice(dishes)
    h = []
    s = []
    if " " in dish:
        dish = " ".join(dish.split())
        x = dish.split(" ")
        h = [''.join(random.sample(x[0], len(x[0])))]
        s = [''.join(random.sample(x[1], len(x[1])))]
    return dish, h, s
numb = None

@tasks.loop(minutes=5)
async def send_question():
    global last_question_timestamp
    global current_question
    global questions
    global m_id

    emojis_list = ["😋", "👌","😔", "🤡", "👽","🤓", "👩", "🍵", "🥶", "😩", "🔫", "☠"] # Customisable
    emojis = " ".join(random.choices(emojis_list, k=3))
    answer = emojis.replace(" ", "")
    dish, h, s= sel_dish()

    new = [''.join(random.sample(dish, len(dish)))]
    num = random.randint(1, 10)
    questions = [
        {
            "question": "Repeat Event",
            "description": f"Quick! Send the word below in chat. No copy pasting! \n\n{dish}",
            "answer": dish
        },
        {
            "question": "GTN Event",
            "description": "I'm thinking of a number between 1-10. What is the number?",
            "answer": num
        },
        {
            "question": "Trivia Event",
            "description": "When did Lenin die? \n\nA. 21 January 1924\nB. 21 January 1934\nC. 21 January 1944\nD. 21 January 1954", #customisable
            "answer": ["a", "A"]
        },
        {
            "question": "Emoji Event",
            "description": f'Quick! Send the emojis below in chat (without spaces). No copy pasting! \n\n{emojis}',
            "answer": answer
        },
        {
            "question": "Unscramble Event",
            "description": f"Quick! Unscramble the word below. \n\n{''.join(h)} {''.join(s)}" if " " in dish else f"Quick! Unscramble the word below. \n\n{''.join(new)}",
            "answer": dish
        }
    ]

    if last_question_timestamp is not None and (datetime.datetime.now() - last_question_timestamp).seconds < 300:
        return
    question = sel_question()
    
    e_channel = await bot.fetch_channel()

    random.shuffle(emojis_list)
    
    em = discord.Embed(title=question["question"], description=question["description"], color=discord.Colour.random())
    em.set_footer(text="The first to answer correctly gets 17 - 50 coins!")

    m = await e_channel.send(embed=em)
    m_id = m.id
    current_question = question["answer"]
    last_question_timestamp = datetime.datetime.now()

    await asyncio.sleep(45)

    if current_question is not None:
        await e_channel.send("Nobody responded in time :(", delete_after=5)
        await m.delete()

    m_id = None


@bot.event
async def on_message(message):
    global current_question
    global m_id
    global numb

    if current_question and message.channel.id == 927224448447299594 and not message.author.bot and message.content != None:

        if str(current_question).isdigit():
            try:
                int_message = int(message.content.strip())
            except ValueError:
                return
            if int_message == current_question:
                coins = random.randint(17, 50)
                await message.channel.send(f"{message.author.mention} got it correct first and has won **{str(coins)} coins**! 🎉", delete_after=5)
                await update_bank_data(message.author, coins=coins)
                async for m in message.channel.history(limit=20):
                    if m.content.isdigit():
                        await m.delete()
                current_question = None
                m = await message.channel.fetch_message(m_id)
                await m.delete()
                await message.delete()

        elif str(message.content.lower()) == str(current_question).lower():
            coins = random.randint(17, 50)
            await message.channel.send(f"{message.author.mention} got it correct first and has won **{str(coins)} coins**! 🎉", delete_after=5)
            await update_bank_data(message.author, coins=coins)
            current_question = None
            m = await message.channel.fetch_message(m_id)
            await m.delete()
            await message.delete()

    await bot.process_commands(message)

@bot.command(hidden=True)
@commands.is_owner()
async def sync(ctx):
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)}commands.")
        await ctx.reply(f"Synced {len(synced)}commands.", delete_after=5)
    except Exception as e:
        print(f"Error syncing commands: {e}")


@bot.event
async def on_ready():
    for file in os.listdir('./cogs'):
        if file.endswith('.py') and file != 'emojis.py':
            await bot.load_extension(f"cogs.{file[:-3]}")
    print(f"Starting up...\nMy username is {bot.user.name} and I'm running with the ID: {bot.user.id}")
    global startTime
    startTime = time.time()
    send_question.start()
    
@bot.tree.command(name='uptime', description="Check the bot\'s latency.")
async def uptime(interaction: discord.Interaction):
    uptime = str(datetime.timedelta(seconds=int(round(time.time()-startTime))))
    await interaction.response.send_message(f'Uptime: {uptime}')

# Running

token = "" # put your token here
bot.run(f"{token}", reconnect=True)
