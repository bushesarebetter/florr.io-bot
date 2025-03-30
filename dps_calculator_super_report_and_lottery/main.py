import discord
import os
import math
from discord.ext.commands.bot import BotBase
from dotenv import load_dotenv
from discord.ext import commands
from autocorrect import autocorrect
from check import check
from report import report
from report import ultra_report
from report import test_report
import requests
from PIL import Image as im
from io import BytesIO
import random

cooldown = 3

load_dotenv('.env') # token

dice_emojis = {
    1: ":one:",
    2: ":two:",
    3: ":three:",
    4: ":four:",
    5: ":five:",
    6: ":six:"
}

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)
bur_add = 1.5
bot_commands = 1181315787517067344


def calc(xp):
  total_xp = xp
  xp_needed = 0
  level = 1
  while True:
    xp_needed = 1000 + (level - 1) * 100
    if xp >= xp_needed:
      level += 1
      xp -= xp_needed
    else:
      xp_needed -= xp
      break
  level -= 1
  return level, xp, xp_needed, total_xp


damage_multiplier = {
    "s": 2187,
    "u": 729,
    "m": 243,
    "l": 81,
    "e": 27,
    "r": 9,
    "un": 3,
    "c": 1
}


class Economy:

  @staticmethod
  def load():
    try:
      with open("players.txt", "r") as file:
        file_content = file.read()
      players = eval(file_content)
      return players
    except FileNotFoundError:
      return {}
    except Exception as e:
      print("An error occurred while loading the file:", e)
      return {}

  @staticmethod
  def save(players):
    with open("players.txt", "w") as file:
      file.write(str(players))

  @staticmethod
  def add_player(id):
    players = Economy.load()
    players[id] = {"money": 0, "reports": 0}
    Economy.save(players)

  @staticmethod
  def parse(id):
    players = Economy.load()
    info = players.get(id)
    if info is not None:
      money = info.get("money", 0)
      reports = info.get("reports", 0)
      return info, money, reports
    else:
      money = 0
      reports = 0
      return info, money, reports

  @staticmethod
  def user_update(id, money_change: int = 0, reports_change: int = 0):
    players = Economy.load()
    players_info = players.get(id)
    if players_info:
      players_info["money"] += money_change
      players_info["reports"] += reports_change
      Economy.save(players)
      return True
    else:
      return False


class Levels:

  @staticmethod
  def load():
    try:
      with open("levels.txt", "r") as file:
        file_content = file.read()
      levels = eval(file_content)
      return levels
    except FileNotFoundError:
      return {}
    except Exception as e:
      print("An error occurred while loading the file:", e)
      return {}

  @staticmethod
  def save(levels):
    with open("levels.txt", "w") as file:
      file.write(str(levels))

  @staticmethod
  def add_player(id):
    levels = Levels.load()
    levels[id] = 1000
    Levels.save(levels)

  @staticmethod
  def parse(id):
    levels = Levels.load()
    if levels.get(str(id)) is None:
      return
    xp = levels.get(str(id))
    level, xp, needed, total = calc(xp)
    return level, xp, needed, total

  @staticmethod
  def user_update(id, xp_change):
    levels = Levels.load()
    levels[id] = levels.get(id, 0) + xp_change
    Levels.save(levels)


def roll_dice():
  roll = random.randint(1, 6)
  return roll


def append_user(id):
  info, money, reports = Economy.parse(id)
  if info is None:
    Economy.add_player(id)
  else:
    return


def report_update(id):
  append_user(id)
  Economy.user_update(id, 100, 1)


@bot.event
async def on_ready():
  print(f'{bot.user} has connected to Discord!')


def calculate_bur(loadout):
  highest_bur_num = 0
  highest_bur = ""
  for petal in loadout:
    if "bur" in petal:
      rarity = petal.replace("bur", "")
      bur_type = damage_multiplier[rarity]
      if bur_type > highest_bur_num:
        highest_bur_num = bur_type
        highest_bur = petal
    else:
      continue
  rarity = highest_bur.replace("bur", "")
  bob = bur_add * damage_multiplier[rarity]
  return bob  # BUR DOESNT STACK


def calculate_iris(loadout):
  highest_iris_num = 0
  total_iris_damage = 0
  maximum_iris = 0
  highest_iris = ""

  for petal in loadout:
    if "iris" in petal:
      rarity = petal.replace("iris", "")
      iris_type = damage_multiplier[rarity]
      if iris_type > highest_iris_num:
        highest_iris_num = iris_type
        highest_iris = petal
  for petal in loadout:
    if "iris" in petal:
      rarity = petal.replace("iris", "")
      iris_type = damage_multiplier[rarity]
      if iris_type == highest_iris_num:
        total_iris_damage += 75 * highest_iris_num
        print("big")
      else:
        total_iris_damage += 5 * iris_type
        print("small")
  return total_iris_damage


def append_user_lvl(id):
  if Levels.parse(id) is None:
    Levels.add_player(id)
  else:
    return


def is_convertible_to_int(s):
  try:
    int(s)
    return True
  except ValueError:
    return False


reload_map = {
    "u": 40,
    "m": 35,
    "l": 31,
    "e": 25,
    "r": 20,
    "un": 14,
    "c": 7,
    "n": 0
}
rotation_map = {"n": 2.5, "c": 2.8, "un": 3.1, "r": 3.4, "e": 3.7, "l": 4}
# BASE_damage, reload, petals_affected
bur_affected_petals = {
    "llight": [1053, 0.8, 3],
    "mlight": [3159, 0.8, 5],
    "ulight": [9477, 0.8, 5],
    "slight": [28431, 0.8, 5],
    "csand": [20, 1.5, 4],
    "unsand": [60, 1.5, 4],
    "rsand": [180, 1.5, 4],
    "esand": [540, 1.5, 4],
    "lsand": [1620, 1.5, 4],
    "msand": [4860, 1.5, 4],
    "usand": [14580, 1.5, 4],
    "ssand": [43740, 1.5, 4],
    "mstinger": [2430, 10, 3],
    "ustinger": [72900, 10, 5],
    "sstinger": [218700, 10, 5],
    "mbstinger": [24300, 5, 3],
    "ubstinger": [72900, 5, 5],
    "sbstinger": [218700, 5, 5],
    "cdahlia": [5, 1.5, 3],
    "undahlia": [15, 1.5, 3],
    "rdahlia": [45, 1.5, 3],
    "edahlia": [135, 1.5, 3],
    "ldahlia": [405, 1.5, 3],
    "mdahlia": [1215, 1.5, 3],
    "udahlia": [3645, 1.5, 3],
    "sdahlia": [10935, 1.5, 3],
    "cpollen": [15, 1.5, 1],
    "unpollen": [45, 1.5, 1],
    "rpollen": [135, 1.5, 2],
    "epollen": [405, 1.5, 3],
    "lpollen": [1215, 1.5, 3],
    "mpollen": [3645, 1.5, 3],
    "upollen": [10935, 1.5, 3],
    "spollen": [32805, 1.5, 3],
    "unorange": [20, 3.5, 3],
    "rorange": [60, 3.5, 3],
    "eorange": [180, 3.5, 3],
    "lorange": [540, 3.5, 3],
    "morange": [1620, 3.5, 3],
    "uorange": [4860, 3.5, 3],
    "sorange": [14580, 3.5, 3]
}
# BASE_DAMAGE, rot_speed_increase
fasters = {
    "cfaster": [8, 0.5],
    "unaster": [24, 0.7],
    "rfaster": [72, 0.9],
    "efaster": [216, 1.1],
    "lfaster": [648, 1.3],
    "mfaster": [1944, 1.5],
    "ufaster": [5832, 1.7],
    "sfaster": [17496, 1.9]
}
# BASE_DAMAGE, reload
# damage is already base to 1
regular_petals = {
    "basic": [10, 2.5],
    "bone": [15, 2.5],
    "bulb": [5, 1],
    "cactus": [5, 1],
    "carrot": [10, 1],
    "claw": [5, 4],
    "clover": [10, 2.5],
    "corn": [5, 10],
    "dandelion": [5, 1],
    "dice": [10 + 10 * 35 * 0.05, 2.5],
    "fangs": [15, 3.5],
    "grapes": [3, 1.5],
    "heavy": [9, 10],
    "iris": [5, 4],
    "jelly": [10, 2.5],
    "leaf": [13, 1.8333333],
    "lightning": [12, 2.5],
    "lotus": [1, 2.5],
    "magnet": [1, 1.5],
    "missile": [25, 1.5],
    "pearl": [15, 2.4],
    "peas": [10, 1.5],
    "pincer": [20, 2.5],
    "plank": [10, 1.5],
    "poo": [5, 2.5],
    "rose": [5, 2.1],
    "rice": [4, 0.1],
    "rock": [15, 4],
    "rubber": [10, 2],
    "salt": [10, 2.5],
    "starfish": [5, 3.5],
    "soil": [10, 2.5],
    "starfish": [5, 1.5],
    "stick": [1, 4],
    "tomato": [37.5, 2.25],
    "talisman": [10, 2.5],  # add stalisman
    "web": [5, 3],
    "wing": [20, 2.5],
    "yucca": [5, 2.5],
    "yinyang": [10, 2],
}
all_petals = [
    "light", "sand", "stinger", "tringer", "stinger", "bstinger", "dahlia",
    "orange", "pollen", "faster", "air", "amulet", "ankh", "antennae", "basil",
    "battery", "bubble", "cotton", "cutter", "disc", "aegg", "begg", "honey",
    "lotus", "mark", "powder", "relic", "root", "shovel", "sponge", "te", "ygg"
]
# coulding find all for amulet, battery, disc, and shovel (potential more I forgot about)
for name, stat in regular_petals.items():
  all_petals.append(name)


def calculate_damage(damage, reload, rotation):
  y = 2 * math.pi - ((rotation * reload) % (2 * math.pi))
  x = y / rotation
  return damage / (reload + x)


@bot.command()
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def dps(ctx, *inpt):
  channel = bot.get_channel(1181315787517067344)
  append_user(ctx.author.id)
  info, money, reports = Economy.parse(ctx.author.id)
  if money >= 50:
    Economy.user_update(ctx.author.id, -50)
  else:
    await channel.send(
        f"{ctx.author.mention} Insufficient funds 50 coins required!")
    await ctx.message.add_reaction("❌")
    return
  if len(inpt) > 13:
    await ctx.send("Too many inputs provided. Maximum is 13.")
    await ctx.message.add_reaction("❌")
    return

  # Separate petals and rarity inputsspaw
  petals = inpt[:len(inpt) - 3]
  rarities = inpt[len(inpt) - 3:len(inpt)]  # Fixed indexing here
  armor = inpt[len(inpt) - 1]
  if rarities[1] not in rotation_map or rarities[0] not in reload_map:
    await ctx.send(
        "Make sure to input valid reload and rotation rarities/speed. Please remember that all rarities should be undercase and shortened (e.g. legendary = l, unusual = un, rare = r, ultra = u, etc). By the way you may have forgotten armor (int value at end)"
    )
    await ctx.message.add_reaction("❌")
    return None
  if is_convertible_to_int(armor):
    armor = int(armor)
  else:
    await ctx.send("Make sure to input valid armor value")
    await ctx.message.add_reaction("❌")
    return None
  reload_reduction = reload_map[rarities[0]]
  rotation_speed = rotation_map[rarities[1]]
  bur_reduct = 0
  total_dps = 0
  yy = False
  for s in petals:
    if "uranium" in s:
      rarity = s.replace("uranium", "")
      total_dps += 30 * damage_multiplier[rarity]
  if any("bur" in s for s in petals):
    bur_reduct = calculate_bur(petals)
  if any("yinyang" in s for s in petals):
    yy = True
  for j in petals:
    if "faster" in j:
      rotation_speed += fasters[j][1]
  for petal in petals:
    if "iris" in petal:
      iris_damage = calculate_iris(petals)
      total_dps += calculate_damage((iris_damage + bur_reduct),
                                    4 * (100 - reload_reduction) / 100,
                                    rotation_speed)
      break
  for petal in petals:
    if petal in bur_affected_petals:
      if yy:
        total_dps += (bur_affected_petals[petal][0] +
                      bur_affected_petals[petal][2] *
                      (bur_reduct - armor)) / (bur_affected_petals[petal][1] *
                                               (100 - reload_reduction))
      else:
        total_dps += calculate_damage(
            bur_affected_petals[petal][0] + bur_affected_petals[petal][2] *
            (bur_reduct - armor),
            bur_affected_petals[petal][1] * (100 - reload_reduction) / 100,
            rotation_speed)
      continue
    elif petal in fasters:
      if yy:
        total_dps += (fasters[petal][0] +
                      (bur_reduct - armor)) / (2.5 *
                                               (100 - reload_reduction) / 100)
      else:
        total_dps += calculate_damage((fasters[petal][0] + bur_reduct),
                                      2.5 * (100 - reload_reduction) / 100,
                                      rotation_speed)
      continue

    for name, stats in regular_petals.items():
      if name in petal:
        rarity = petal.replace(name, "")
        damage = stats[0] * damage_multiplier[rarity] + bur_reduct - armor
        if yy:
          total_dps += damage / stats[1] * (100 - reload_reduction) / 100
        else:
          total_dps += calculate_damage(
              damage, stats[1] * (100 - reload_reduction) / 100,
              rotation_speed)
  bg_url = "https://raw.githubusercontent.com/PowerSpyy/calculator_app/main/bg.png"
  bg_response = requests.get(bg_url)
  if bg_response.status_code == 200:
    bg = im.open(BytesIO(bg_response.content))
  else:
    print(
        f"Failed to load background image. Status code: {bg_response.status_code}"
    )

  petal_place_x = 82
  petal_place_y = 51
  for petal in petals:
    if petal == "bpinger":
      petal = "ubstinger"
    elif petal == "sbpinger":
      petal = "sbstinger"
    elif petal == "btringer":
      petal = "mbstinger"
    elif petal == "tringer":
      petal = "mstinger"
    elif petal == "pinger":
      petal = "ustinger"
    elif petal == "spinger":
      petal = "sstinger"
    elif petal == "blood stinger":
      petal = "bstinger"
    petal_url = f"https://raw.githubusercontent.com/PowerSpyy/calculator_app/main/{petal}.png"
    petal_response = requests.get(petal_url)
    if petal_response.status_code == 200:
      petal_img = im.open(BytesIO(petal_response.content))
      petal_img = petal_img.resize((132, 132))
      bg.paste(petal_img, (petal_place_x, petal_place_y))
    else:
      print(f"Image file {petal}.png not found on GitHub.")
    petal_place_x += 150  # Increment x-coordinate outside the if condition

  bg.save("final_image.png")
  print("Final image saved as 'final_image.png'")

  bg.save("final_image.png")
  if total_dps < 0:
    total_dps = 0
  await ctx.send(str(total_dps))
  print(total_dps)
  with open("final_image.png", "rb") as file:
    await ctx.send(file=discord.File(file))
    await ctx.message.add_reaction("✅")


@bot.command()
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def s(ctx, *inpt):
  user = ctx.author
  user_id = user.id
  money_channel = bot.get_channel(1181315787517067344)
  channel = bot.get_channel(1181315787517067344)
  no_reports = discord.utils.get(ctx.guild.roles, name="no reports")
  if no_reports in user.roles:
    await channel.send(f"You do not have permission to use this command")
  elif no_reports is None or no_reports not in user.roles:
    server1 = inpt[-1]
    mob = " ".join(inpt[:-1])
    if mob == '':
      embed = discord.Embed(title="Error",
                            description="Invalid",
                            colour=discord.Color.red())
      await ctx.send(embed=embed)
    else:
      server = await check(ctx, server1)
      if server == 'invalid':
        pass
      elif server == 'na' or server == 'eu' or server == 'as':
        userinp = mob
        mob = await autocorrect(mob)
        user = ctx.message.author
        await report(ctx, mob, server, user, userinp)
        report_update(ctx.author.id)


@bot.command(aliases=["N", "NA", "Na", "nA", "na", "us", "Juliet", "juliet"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def n(ctx, *inpt):
  user = ctx.author
  user_id = user.id
  money_channel = bot.get_channel(1181315787517067344)
  channel = bot.get_channel(1181315787517067344)
  no_reports = discord.utils.get(ctx.guild.roles, name="no reports")
  if no_reports in user.roles:
    await channel.send(f"You do not have permission to use this command")
  elif no_reports is None or no_reports not in user.roles:
    await ctx.message.add_reaction("✅")
    server = "na"
    mob = " ".join(inpt)
    if mob == '':
      embed = discord.Embed(title="Error",
                            description="Invalid",
                            colour=discord.Color.red())
      await ctx.send(embed=embed)
    else:
      userinp = mob
      mob = await autocorrect(mob)
      user = ctx.message.author
      await report(ctx, mob, server, user, userinp)
      report_update(ctx.author.id)


@bot.command(
    aliases=["EU", "E", "eU", "europe", "Europe", "Eu", "Romeo", "romeo"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def e(ctx, *inpt):
  user = ctx.author
  user_id = user.id
  money_channel = bot.get_channel(1181315787517067344)
  channel = bot.get_channel(1181315787517067344)
  no_reports = discord.utils.get(ctx.guild.roles, name="no reports")
  if no_reports in user.roles:
    await channel.send(f"You do not have permission to use this command")
  elif no_reports is None or no_reports not in user.roles:
    await ctx.message.add_reaction("✅")
    server = "eu"
    mob = " ".join(inpt)
    if mob == '':
      embed = discord.Embed(title="Error",
                            description="Invalid",
                            colour=discord.Color.red())
      await ctx.send(embed=embed)
    else:
      userinp = mob
      mob = await autocorrect(mob)
      user = ctx.message.author
      await report(ctx, mob, server, user, userinp)
      report_update(ctx.author.id)


@bot.command(aliases=["as", "As", "aS", "asia", "Asia", "Sierra", "sierra"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def a(ctx, *inpt):
  user = ctx.author
  user_id = user.id
  money_channel = bot.get_channel(1181315787517067344)
  channel = bot.get_channel(1181315787517067344)
  no_reports = discord.utils.get(ctx.guild.roles, name="no reports")
  if no_reports in user.roles:
    await channel.send(f"You do not have permission to use this command")
  elif no_reports is None or no_reports not in user.roles:
    await ctx.message.add_reaction("✅")
    server = "as"
    mob = " ".join(inpt)
    if mob == '':
      embed = discord.Embed(title="Error",
                            description="Invalid",
                            colour=discord.Color.red())
      await ctx.send(embed=embed)
    else:
      userinp = mob
      mob = await autocorrect(mob)
      user = ctx.message.author
      await report(ctx, mob, server, user, userinp)
      report_update(ctx.author.id)


@bot.command(aliases=["ultra", "Ultra", "ul", "Ul", "uL"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def u(ctx, *inpt):
  user = ctx.author
  channel = bot.get_channel(1181315787517067344)
  no_reports = discord.utils.get(ctx.guild.roles, name="no reports")
  if no_reports in user.roles:
    await channel.send(f"You do not have permission to use this command")
  elif no_reports is None or no_reports not in user.roles:
    server1 = inpt[-1]
    mob = " ".join(inpt[:-1])
    if mob == '':
      embed = discord.Embed(title="Error",
                            description="Invalid",
                            colour=discord.Color.red())
      await ctx.send(embed=embed)
    else:
      server = await check(ctx, server1)
      if server == 'invalid':
        pass
      elif server == 'na' or server == 'eu' or server == 'as':
        userinp = mob
        mob = await autocorrect(mob)
        user = ctx.message.author
        await ultra_report(ctx, mob, server, user, userinp)


@bot.command(aliases=["t"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def test(ctx, *inpt):
  user = ctx.author
  channel = bot.get_channel(1181315787517067344)
  no_reports = discord.utils.get(ctx.guild.roles, name="no reports")
  if user == ctx.author:
    await ctx.message.add_reaction("✅")
    server = "Not Applicable"
    mob = " ".join(inpt)
    if mob == '':
      embed = discord.Embed(title="Error",
                            description="Invalid",
                            colour=discord.Color.red())
      await ctx.send(embed=embed)
    else:
      userinp = mob
      mob = await autocorrect(mob)
      user = ctx.message.author
      await test(ctx, mob, server, user, userinp)


@bot.command(aliases=["addmoney", "addcash"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def give(ctx, user_info=None, amount: int = 0):
  if user_info is None:
    user = ctx.author
  else:
    if user_info.startswith("<@") and user_info.endswith(">"):
      user_id = user_info.strip("<@!>")
      user = ctx.guild.get_member(int(user_id))
    else:
      user = discord.utils.get(ctx.guild.members, display_name=user_info)
      if user is None:
        user = discord.utils.get(ctx.guild.members, name=user_info)
        if user is None:
          await ctx.send(
              f"{ctx.author.mention} User not found. Please try again.")
          return
  append_user(user.id)
  if ctx.author.guild_permissions.administrator:
    append_user(user.id)
    # The function checks if the user is registered and if not it adds them
    Economy.user_update(user.id, money_change=amount)
    # Add to the user's balance
    await ctx.message.add_reaction("✅")
    await ctx.send(f"Gave {amount} coins to {user.name}!")
  else:
    await ctx.send("You don't have permission to use this command.")


@bot.command()
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def addreps(ctx, user_info=None, amount: int = 0):
  if user_info is None:
    user = ctx.author
  else:
    # Check if the user_info is a mention
    if user_info.startswith("<@") and user_info.endswith(">"):
      # Extract user ID from mention
      user_id = user_info.strip("<@!>")
      user = ctx.guild.get_member(int(user_id))
    else:
      # Find user by display name or username
      user = discord.utils.get(ctx.guild.members, display_name=user_info)
      if user is None:
        user = discord.utils.get(ctx.guild.members, name=user_info)

    # Check if user is still None
    if user is None:
      await ctx.send(f"{ctx.author.mention} User not found. Please try again.")
      print(user_info)
      return
    append_user(user.id)
  if ctx.author.guild_permissions.administrator:
    append_user(user.id)
    Economy.user_update(user.id, reports_change=amount)
    await ctx.message.add_reaction("✅")
    await ctx.send(f"Increased {user.name}'s reports by {amount}!")
  else:
    await ctx.send(f"Access denied! You do not have the neccessary permisions."
                   )


@bot.command()
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def cf(ctx, choice, amount: int = 5):
  channel = bot.get_channel(bot_commands)
  append_user(ctx.author.id)
  if amount < 5:
    await channel.send(f"You must bet a minimum of 5 coins <@{ctx.author.id}>!"
                       )
    return
  author_info, author_money, author_reports = Economy.parse(ctx.author.id)
  if author_money < amount:
    await channel.send(f"Insufficient funds. Try again <@{ctx.author.id}>.")
    return
  choices = ["h", "t"]
  winning = random.choice(choices)
  if choice == winning:
    Economy.user_update(ctx.author.id, amount)
    await channel.send(f"<@{ctx.author.id}> You won {amount} coins!")
  elif choice == 'h' or choice == 't':
    Economy.user_update(ctx.author.id, -int(amount))
    await channel.send(f"<@{ctx.author.id}> You lost {amount} coins!")
  else:
    await channel.send(
        f"<@{ctx.author.id}> Invalid input try again with h or t for heads and tails!"
    )


@bot.command(aliases=["shops", "sho"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def shop(ctx, *, user_info=None):
  channel = bot.get_channel(bot_commands)
  await ctx.message.add_reaction("✅")
  await channel.send(
      f"{ctx.author.mention} \nAccess to super spawns chatting: 2.5k coins \nCustom role (one): 1k coins \nAccess to VIP-CHAT: 3k Coins"
  )


@bot.command(aliases=["p", "bal", "balance", "reps", "reports"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def profile(ctx, *, user_info=None):
  channel = bot.get_channel(bot_commands)
  if user_info is None:
    user = ctx.author
  else:
    if user_info.startswith("<@") and user_info.endswith(">"):
      user_id = user_info.strip("<@!>")
      user = ctx.guild.get_member(int(user_id))
    else:
      user = discord.utils.get(ctx.guild.members, display_name=user_info)
      if user is None:
        user = discord.utils.get(ctx.guild.members, name=user_info)
        if user is None:
          await ctx.send(
              f"{ctx.author.mention} User not found. Please try again.")
          return
  print(user.id)
  append_user(user.id)
  append_user_lvl(user.id)
  user_info, money, reports = Economy.parse(user.id)
  if user_info:
    level, xp, needed, total = Levels.parse(user.id)
    embed = discord.Embed(title=f"Profile - {user.name}",
                          color=discord.Color.blue())
    embed.add_field(name="Money", value=f"{money} coins", inline=False)
    embed.add_field(name="Reports", value=f"{reports} reports", inline=False)
    embed.add_field(name="Level", value=f"{level}", inline=True)
    avatar_url = user.avatar if user.avatar else ctx.guild.icon.url
    embed.set_thumbnail(url=avatar_url)
    await ctx.message.add_reaction("✅")
    await channel.send(f"{ctx.author.mention}")
    await channel.send(embed=embed)
  else:
    await channel.send(f"{ctx.author.mention} User not found in the database.")


@bot.command(aliases=["r", "rol"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def roll(ctx, amount: int = 10):
  channel = bot.get_channel(bot_commands)
  user = ctx.author
  print(ctx.author.id)
  append_user(ctx.author.id)

  # Ensure the bet amount is within the allowed range
  if amount < 10:
    await channel.send(
        f"{ctx.author.mention} Roll has a minimum bet of 10 coins!")
    return
  if amount > 5000:
    await channel.send(
        f"{ctx.author.mention} Maximum bet is 5000. Changed your bet to 5000!")
    amount = 5000

  # Retrieve user's information from the economy system
  info, money, reps = Economy.parse(user.id)
  if info is None:
    await channel.send(f"{ctx.author.mention} Error!")
    return

  # Check if the user has sufficient funds
  if amount > money:
    await channel.send(f"{ctx.author.mention} Insufficient funds!")
    return

  # Roll the dice for the user and the bot
  dice_1 = roll_dice()
  dice_2 = roll_dice()
  dice_3 = roll_dice()
  dice_4 = roll_dice()
  user_roll = dice_1 + dice_2
  bot_roll = dice_3 + dice_4

  # Create an embed to display the roll result
  embed = discord.Embed(title="Roll Result",
                        color=discord.Color.green()
                        if bot_roll < user_roll else discord.Color.red())

  # Add fields for the user's roll and the bot's roll, using emojis
  embed.add_field(
      name="Your Roll",
      value=f"{dice_emojis[dice_1]} {dice_emojis[dice_2]}\nTotal: {user_roll}",
      inline=True)
  embed.add_field(
      name="Spinger's Roll",
      value=f"{dice_emojis[dice_3]} {dice_emojis[dice_4]}\nTotal: {bot_roll}",
      inline=True)

  # Initialize winnings to 0
  winnings = 0

  # Check the outcome of the roll and update user's balance accordingly
  if bot_roll > user_roll:
    Economy.user_update(user.id, -amount)
    embed.add_field(name="Result", value=f"You lose {amount}!", inline=False)
  elif bot_roll == user_roll:
    embed.add_field(name="Result",
                    value="It's a tie! No gain or loss.",
                    inline=False)
  else:
    win_percent = (((275 / 3) * user_roll) - (77 * bot_roll)) / (2 * math.pi)
    winnings = int(amount * round(win_percent) / 100)
    Economy.user_update(user.id, winnings)
    embed.add_field(name="Result",
                    value=f"You win {round(win_percent)}%!",
                    inline=False)
    embed.add_field(name="Balance Increase",
                    value=f"Your balance has increased by {winnings} coins.",
                    inline=False)

  # Display the new balance
  embed.add_field(
      name="New Balance",
      value=
      f"{money - amount if bot_roll > user_roll else money + winnings} coins",
      inline=False)

  # Send the embed with the roll result to the channel
  await ctx.message.add_reaction("✅")
  await channel.send(user.mention, embed=embed)


@bot.command()
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def lottery(ctx, amount: int = 0):
  winnings = 0
  channel = bot.get_channel(bot_commands)
  user = ctx.author

  with open("lottery.txt", "r") as lottery:
    winnings = int(lottery.read())

  append_user(user.id)
  info, bal, reps = Economy.parse(user.id)
  mention = user.mention

  if amount > bal:
    await channel.send(f"{mention} Insufficient funds!")
    return

  if amount < 5:
    await channel.send(f"{mention} Minimum lottery entry is 5 coins!")
    return

  max = round((winnings * math.e) / (45 * math.pi))
  winrate = round(amount / (math.e * math.pi)) / (max / 14)

  # Ensure winrate and max are not rounded to 0
  while round(winrate) == 0 or round(max) == 0:
    winrate *= 10
    max *= 10

  winrate = round(winrate)
  max = round(max)

  if winnings >= 10000 and amount >= 100:
    max = winrate * 5

  print(f"Max: {max}, Winrate: {winrate}")

  if random.randint(1, max) <= winrate:
    await ctx.message.add_reaction("✅")
    Economy.user_update(user.id, money_change=int(winnings))
    await channel.send(
        f"{mention} Congratulations! You won the lottery and received {winnings} coins!"
    )
    with open("lottery.txt", "w") as file:
      file.write(str(250))
  else:
    await ctx.message.add_reaction("✅")
    Economy.user_update(user.id, money_change=-int(amount))
    await channel.send(f"{mention} You lost the lottery.")
    winnings = winnings + amount
    await channel.send(f"New prize: {winnings}")
    with open("lottery.txt", "w") as file:
      file.write(str(winnings))


@bot.command(aliases=["leaderboard", "LB", "Lb", "lB"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def lb(ctx, type, *y):
  channel = bot.get_channel(bot_commands)
  mention = ctx.author.mention
  file = Economy.load()
  leaderboard = {}

  if type == "money" or type == "balance":
    sorted_file = sorted(file.items(),
                         key=lambda x: x[1]["money"],
                         reverse=True)
    embed = discord.Embed(title="Cash Leaderboard", color=0x0099ff)
    embed.set_thumbnail(url=ctx.guild.icon.url)

    position = 1
    for player_id, player_info in sorted_file[:10]:
      embed.add_field(
          name=f"#{position}. {ctx.guild.get_member(int(player_id))}",
          value=f"Balance: {player_info['money']}",
          inline=False)
      position += 1
    await channel.send(embed=embed)
  elif type == "reports" or type == "reps":
    sorted_file = sorted(file.items(),
                         key=lambda x: x[1]["reports"],
                         reverse=True)
    embed = discord.Embed(title="Reports Leaderboard", color=0x0099ff)
    embed.set_thumbnail(url=ctx.guild.icon.url)

    position = 1
    for player_id, player_info in sorted_file[:10]:
      embed.add_field(
          name=f"#{position}. {ctx.guild.get_member(int(player_id))}",
          value=f"Reports: {player_info['reports']}",
          inline=False)
      position += 1
    await channel.send(embed=embed)
  elif type == "levels" or type == "lvls" or type == "lvl" or type == "level":
    file = Levels.load()
    sorted_file = sorted(file.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(title="Level Leaderboard", color=0x0099ff)
    embed.set_thumbnail(url=ctx.guild.icon.url)

    position = 1
    for player_id, player_info in sorted_file[:10]:
      level, xp, needed, total_xp = Levels.parse(player_id)
      print(level, xp)
      embed.add_field(
          name=f"#{position}. {ctx.guild.get_member(int(player_id))}",
          value=f"Level: {level}",
          inline=False)
      position += 1
    await ctx.message.add_reaction("✅")
    await channel.send(f"{mention}", embed=embed)

  else:
    await ctx.message.add_reaction("✅")
    await channel.send(f"{mention}")
    await channel.send(
        "Invalid input try again with money, reports, or levels!")


@bot.event
async def on_message(message):
  await bot.process_commands(message)
  if message.author.bot:
    return

  append_user_lvl(message.author.id)
  try:
    Levels.user_update(str(message.author.id), 50)
    print("complete")
  except Exception as e:
    print(f"An error occurred: {e}")


@bot.command(aliases=["lvls", "level", "levels"])
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def lvl(ctx, user_info):
  channel = bot.get_channel(bot_commands)
  if user_info is None:
    user = ctx.author
  else:
    if user_info.startswith("<@") and user_info.endswith(">"):
      user_id = user_info.strip("<@!>")
      user = ctx.guild.get_member(int(user_id))
    else:
      user = discord.utils.get(ctx.guild.members, display_name=user_info)
      if user is None:
        user = discord.utils.get(ctx.guild.members, name=user_info)
        if user is None:
          await ctx.send(
              f"{ctx.author.mention} User not found. Please try again.")
          return
  append_user(user.id)
  append_user_lvl(user.id)
  level, xp, needed, total = Levels.parse(user.id)
  print(level)
  embed = discord.Embed(title=f"Level - {user.name}",
                        color=discord.Color.blurple())
  embed.set_thumbnail(url=f"{user.avatar.url}")
  embed.add_field(name="Level", value=f"{level}", inline=False)
  embed.add_field(name="Total XP", value=f"{total}", inline=False)
  embed.add_field(name="XP until next level", value=f"{needed}", inline=False)
  await ctx.message.add_reaction("✅")
  await channel.send(f"{ctx.author.mention}")
  await channel.send(embed=embed)


@bot.command()
@commands.cooldown(1, cooldown, commands.BucketType.user)
async def gift(ctx, user_info, amount: int = 0):
  channel = bot.get_channel(bot_commands)
  mention = ctx.author.mention
  if amount < 0:
    await channel.send(f"{mention}")
    await channel.send("Gift must be a positive number!")
    return
  info, money, reports = Economy.parse(ctx.author.id)
  if amount > money:
    await channel.send(f"{mention}")
    await channel.send("Insufficient funds!")
    return
  if user_info is None:
    await channel.send(f"{mention}")
  else:
    if user_info.startswith("<@") and user_info.endswith(">"):
      user_id = user_info.strip("<@!>")
      user = ctx.guild.get_member(int(user_id))
    else:
      user = discord.utils.get(ctx.guild.members, display_name=user_info)
      if user is None:
        user = discord.utils.get(ctx.guild.members, name=user_info)
        if user is None:
          await channel.send(
              f"{ctx.author.mention} User not found. Please try again.")
          return
  append_user(user.id)
  Economy.user_update(ctx.author.id, -int(amount))
  Economy.user_update(user.id, int(amount))
  await ctx.message.add_reaction("✅")
  await channel.send(f"{user.mention}")
  await channel.send(f"{mention} has sent you {amount}!")


@bot.command(aliases=[""])
@commands.cooldown(1, 15, commands.BucketType.user)
async def register(ctx):
  append_user(ctx.author.id)
  if Economy.parse(ctx.author.id) is not None:
    await ctx.send("Registration Successful!")
  else:
    await ctx.send("Registration Failed.")


@cf.error
async def cf_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@lottery.error
async def lottery_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@profile.error
async def profile_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@roll.error
async def roll_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@a.error
async def a_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@n.error
async def n_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@e.error
async def e_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@register.error
async def register_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@lb.error
async def lb_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@dps.error
async def dps_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@lvl.error
async def lvl_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@gift.error
async def gift_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


@s.error
async def s_error(ctx, error):
  if isinstance(error, commands.CommandOnCooldown):
    await ctx.send(
        f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds."
    )


bot.run(os.getenv('TOKEN'))
