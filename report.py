from fuzzywuzzy import fuzz, process
import discord
from discord.ext import commands
import os
import subprocess
import sys
import asyncio

bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())
sping = 1179669500862410802
dev_role_id = 1192275009767485531
bot_token = "REDACTED"
mobs = [
    "Hel Beetle", "Beetle", "Bubble", "Bush", "Cactus", "Centipede", "Crab",
    "Dandelion", "Fly", "Hornet", "Jellyfish", "Ladybug", "Leech", "Mantis",
    "Moth", "Queen Ant", "Fire Queen Ant", "Roach", "Rock", "Sandstorm",
    "Scorpion", "Shell", "Spider", "Starfish", "Termite Overmind", "Wasp",
    "Ant Egg", "Ant Hole", "Baby Ant", "Baby Fire Ant", "Baby Termite",
    "Bumblebee", "Evil Centipede", "Digger", "Fire Ant Burrow", "Fire Ant Egg",
    "Firefly", "Shiny Ladybug", "Dark Ladybug", "Soldier Fire Ant",
    "Soldier Ant", "Soldier Termite", "Sponge", "Square", "Termite Egg",
    "Termite Mound", "Worker Ant", "Fire Worker Ant", "Worker Termite", "Bee",
    "Leafbug", "Desert Centipede"
]


def get_mob_link(mob_name):
  mob_link_prefix = "https://github.com/Sniperopo/florr/blob/main/Super/"
  mob_name = mob_name.replace(" ", "%20")
  mob_link_ending = ".png?raw=true"
  mob_link = mob_link_prefix + mob_name + mob_link_ending
  return mob_link


mistakes = {
    "fqueen": "Fire Queen Ant",
    "queenf": "Fire Queen Ant",
    "fqa": "Fire Queen Ant",
    "fq": "Fire Queen Ant",
    "hel": "Hel Beetle",
    "hell": "Hel Beetle",
    "hb": "Hel Beetle",
    "hbe": "Hel Beetle",
    "hellb": "Hel Beetle",
    "hbeetle": "Hel Beetle",
    "ss": "Sandstorm",
    "helly": "Jellyfish",
    "ovm": "Termite Overmind",
    "hrl": "Hel Beetle",
    "hwl": "Hel Beetle",
    "fireant": "Fire Queen Ant",
    "qfa": "Fire Queen Ant",
    "jely": "Jellyfish",
    "shel": "Shell",
    "firquen": "Fire Queen Ant",
    "quen": "Queen Ant",
    "overmimd": "Termite Overmind",
    "fqeen": "Fire Queen Ant",
    "sandstorm": "Sandstorm",
    "dcenti": "Desert Centipede",
    "dcent": "Desert Centipede",
    "dc": "Desert Centipede",
    "hormet": "Hornet",
    "queef": "Fire Queen Ant",
    "ecenti": "Evil Centipede",
    "queen fire": "Fire Queen Ant",
    "hellbeetle": "Hel Beetle",
    "qf": "Fire Queen Ant",
    "deceti": "Desert Centipede",
    "sfq": "Fire Queen Ant",
    "stra": "Starfish",
    "qa": "Queen Ant",
    "bfa": "Baby Fire Ant",
    "fba": "Baby Fire Ant",
    "bt": "Baby Termite",
    "bterm": "Baby Termite",
    "be": "Bee",
    "ae": "Ant Egg",
    "ah": "Ant Hole",
    "ba": "Baby Ant",
    "bb": "Bumblebee",
    "dlady": "Dark Ladybug",
    "ecenti": "Evil Centipede",
    "fab": "Fire Ant Burrow",
    "fah": "Fire Ant Burrow",
    "fire and hole": "Fire Ant Burrow",
    "fae": "Fire Ant Egg",
    "fantegg": "Fire Ant Egg",
    "sa": "Soldier Ant",
    "sfa": "Soldier Fire Ant",
    "fsa": "Soldier Fire Ant",
    "st": "Soldier Termite",
    "sterm": "Soldier Termite",
    "wa": "Worker Ant",
    "wfa": "Worker Fire Ant",
    "wt": "Worker Termite"
}


def correction(report):
  report = report.lower()
  highest = report
  score = 0
  check = 0
  for key in mistakes.keys():
    if report == key.lower():
      highest = mistakes[key]
      check = 1
      score = fuzz.ratio(report, highest)
      return highest, f"{score}%"
  if check == 0:
    closest = process.extractOne(report, mobs)
    ratio = fuzz.ratio(report, closest[0])
    return closest[0], f"{ratio}%"


check_mark = '✅'
cross_mark = '❌'
bot_commands = 1185737447276019813
shiny_pings = 1200577342280573008


async def embed(channel, title, message_url, superPinger, pfp_url,
                superMob_url, superMob_name, user_input, similarity_rate,
                word):
  embed = discord.Embed(title=title,
                        description="",
                        color=discord.Color.blue())
  embed.set_author(name=superPinger, icon_url=pfp_url)
  embed.set_thumbnail(url=superMob_url)
  embed.add_field(name=superMob_name,
                  value="Input: `" + user_input + "`" + "\n" + word +
                  similarity_rate,
                  inline=False)
  await channel.send(embed=embed)


@bot.command()
async def n(ctx, *y):
  rep = ''.join(y)
  most_likely, perc = correction(rep)
  channel = bot.get_channel(sping)
  author = ctx.author
  username = author.display_name
  user = author.name
  img = author.avatar
  await ctx.message.add_reaction(check_mark)
  await channel.send(f"<@&1200284440258162688> NA Super {most_likely}")
  await embed(channel, most_likely, "https://google.com", user, img,
              get_mob_link(most_likely), "", rep, perc, "Similarity Rate: ")


@bot.command()
async def e(ctx, *y):
  rep = ''.join(y)
  most_likely, perc = correction(rep)
  channel = bot.get_channel(sping)
  author = ctx.author
  username = author.display_name
  user = author.name
  img = author.avatar
  await ctx.message.add_reaction(check_mark)
  await channel.send(f"<@&1200284440258162688> EU Super {most_likely}")
  await embed(channel, most_likely, "https://google.com", user, img,
              get_mob_link(most_likely), "", rep, perc, "Similarity Rate: ")


@bot.command()
async def a(ctx, *y):
  rep = ''.join(y)
  most_likely, perc = correction(rep)
  channel = bot.get_channel(sping)
  author = ctx.author
  username = author.display_name
  user = author.name
  img = author.avatar
  await ctx.message.add_reaction(check_mark)
  await channel.send(f"<@&1200284440258162688> AS Super {most_likely}")
  await embed(channel, most_likely, "https://google.com", user, img,
              get_mob_link(most_likely), "", rep, perc, "Similarity Rate: ")


@bot.command()
async def test(ctx, *y):
  channel = bot.get_channel(bot_commands)
  rep = ''.join(y)

  most_likely, perc = correction(rep)
  author = ctx.author
  username = author.display_name
  user = author.name
  id = author.id
  img = author.avatar

  mention = f"<@{id}>"
  await ctx.message.add_reaction(check_mark)
  await embed(channel, most_likely, "https://google.com", user, img,
              get_mob_link(most_likely), "", rep, perc, "Similarity Rate: ")


@bot.command()
async def shiny(ctx, *y):
  channel = bot.get_channel(shiny_pings)
  rep = ''.join(y)
  originalrep = rep
  rep = rep.replace("na", "n")
  rep = rep.replace("us", "n")
  rep = rep.replace("eu", "e")
  rep = rep.replace("as", "a")
  rep = rep.replace("legendary", "l")
  rep = rep.replace("mythic", "m")
  rep = rep.replace("ultra", "u")
  author = ctx.author
  username = author.display_name
  user = author.name
  id = author.id
  img = author.avatar
  rarity = rep[0] if rep[0] == "l" or rep[0] == "m" or rep[0] == "u" else rep[1]
  rarity = rarity.replace("l", "Legendary")
  rarity = rarity.replace("m", "Mythic")
  rarity = rarity.replace("u", "Ultra")
  rarity_url = "https://static.wikia.nocookie.net/official-florrio/images/1/15/Ladybug_%28Yellow%29_%28Legendary%29.png/revision/latest?cb=20220906022109" if rarity == "Legendary" else "https://static.wikia.nocookie.net/official-florrio/images/a/a8/Ladybug_%28Yellow%29_%28Mythic%29.png/revision/latest?cb=20220906022111" if rarity == "Mythic" else "https://ih1.redbubble.net/image.2329454196.0514/raf,360x360,075,t,fafafa:ca443f4786.jpg"

  realm = rep[0] if rep[0] == "n" or rep[0] == "e" or rep[0] == "a" else rep[1]
  area = rep[2:] if len(rep) > 2 else "d4 probably"
  print(rep)
  await ctx.message.add_reaction(check_mark)
  await embed(channel, rarity + " Shiny Ladybug", "https://google.com", user,
              img, rarity_url, "", originalrep, area, "Area: ")


@bot.command()
async def code(ctx):
  dev = discord.utils.get(ctx.guild.roles, id=dev_role_id)
  if dev and dev in ctx.author.roles:
    current_filename = os.path.abspath(__file__)
    await ctx.author.send("Here is the code:",
                          file=discord.File(current_filename))
    await ctx.message.add_reaction(check_mark)
  else:
    await ctx.send(
        "You do not have the required permisions to access the code.")
    await ctx.message.add_reaction(cross_mark)


@bot.command()
async def update(ctx):
  dev = discord.utils.get(ctx.guild.roles, id=dev_role_id)
  if dev and dev in ctx.author.roles:
    await ctx.send("Please DM me the Python file to update the bot's code.")
    await ctx.author.send("Send me the code here!")
    try:
      dm_channel = await ctx.author.create_dm()
      file_message = await bot.wait_for(
          'message',
          check=lambda m: m.author == ctx.author and m.channel == dm_channel
          and m.attachments,
          timeout=60)
      attachment = file_message.attachments[0]

      if attachment.filename.endswith('.py'):
        current_filename = os.path.abspath(__file__)
        file_content = await attachment.read()
        with open(current_filename, 'wb') as f:
          f.write(file_content)

        await ctx.send("Code updated successfully. Restarting the bot...")

        subprocess.run([sys.executable, current_filename])

        await ctx.send(
            "Code has been run successfully! Terminating previous bot instance."
        )

        os._exit(0)

      else:
        await ctx.send("Invalid file type. Please send a Python (.py) file.")
    except asyncio.TimeoutError:
      await ctx.send("Update process timed out.")
      await ctx.author.send("The update process has timed out :sob:")
  else:
    await ctx.send(
        "You do not have the required permissions to use this command.")


bot.run(bot_token)
