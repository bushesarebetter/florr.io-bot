import datetime
import discord

spawn_areas = {
    "Garden": "maze, cf6, cf7, cf5, cf2,  cf3, cf1",
    "Jungle": "j1, j2, j3, j4, j5",
    "Ocean":
    "o6, o4, o7, o3/Ocean Maze, Jellyfish Fields, o2, o4, o1, crab kingdom",
    "Desert": "d1, d5, d4, d2, d3",
    "Sewers": "cs1, cs2, cs3, cs4",
    "Shiny Ladybug": "d4",
    "Centipede": "cf6",
    "Ant Hell": "Ant Hell 2",
    "Fire Ant Hell": "Ant Hell 1",
    "Termite Ant Hell": "Ant Hell 3",
    "Hel": "Hell",
    "Dandelion": "cf6, cf7",
}
mob_areas = {
    "Garden": [
        "Bee", "Rock", "Centipede", "Hornet", "Ant Hole", "Bumble Bee",
        "Ladybug"
    ],
    "Jungle":
    ["Bush", "Evil Centipede", "Leafbug", "Mantis", "Wasp", "Termite Mound"],
    "Ocean": ["Shell", "Starfish", "Sponge", "Leech", "Jellyfish", "Bubble"],
    "Desert": [
        "Cactus", "Beetle", "Sandstorm", "Desert Centipede", "Fire Ant Burrow",
        "Digger", "Scorpion"
    ],
    "Sewers": ["Roach", "Spider", "Fly", "Moth"],
    "Shiny Ladybug": ["Shiny", "Shiny Ladybug"],
    "Centipede": ["Centipede"],
    "Ant Hell": ["Queen Ant", "Soldier Ant", "Worker Ant", "Ant Egg"],
    "Fire Ant Hell": [
        "Fire Queen Ant", "Fire Worker Ant", "Baby Fire Ant", "Fire Ant Egg",
        "Soldier Fire Ant"
    ],
    "Termite Ant Hell": [
        "Termite Overmind", "Baby Termite", "Soldier Termite", "Termite Egg",
        "Woker Termite"
    ],
    "Hel": ["Hel Beetle"],
    "Dandelion": ["Dandelion"]
}


class simpleview(discord.ui.View):

  def __init__(self, *mob_reported, **kwargs):
    super().__init__(**kwargs)
    self.mob_reported = mob_reported
    self.spawn_area = None

  fake_reps = 0
  users = []
  activated = False

  @discord.ui.button(label=f"Fake: {fake_reps}",
                     style=discord.ButtonStyle.gray)
  async def fake(self,
                 interaction: discord.Interaction,
                 button=discord.ui.Button):
    if interaction.user.id in self.users:
      await interaction.response.send_message("You have already reported!",
                                              ephemeral=True)
    else:
      self.fake_reps += 1
      self.users.append(interaction.user.id)
      if self.fake_reps >= 3 and not self.activated:
        button.style = discord.ButtonStyle.red
        self.activated = True
      button.label = f"Fake: {self.fake_reps}"
      await interaction.response.edit_message(view=self)

  @discord.ui.button(label=f"Mob Locations", style=discord.ButtonStyle.gray)
  async def area(self,
                 interaction: discord.Interaction,
                 button=discord.ui.Button):
    spawn_area = ""
    for name in mob_areas:
      for mob in mob_areas[name]:
        if mob == self.mob_reported[0]:
          spawn_area = spawn_areas[name]
    await interaction.response.send_message(
        "Areas where " + self.mob_reported[0] + " can spawn: " + spawn_area,
        ephemeral=True)


async def report(ctx, mob, server, user, userinp):
  view = simpleview(mob)
  super_channel = discord.utils.get(ctx.guild.channels, name="𝗦𝗨𝗣𝗘𝗥-𝗦𝗣𝗔𝗪𝗡𝗦")
  server = str(server)
  embed = discord.Embed(
      title=f"**{server.upper()}: Super {str(mob).title()}**",
      description="User input: `{}`".format(ctx.message.content),
      colour=discord.Color.from_rgb(50, 205, 50))
  embed.timestamp = datetime.datetime.now()
  embed.set_author(name="Reported by " + str(ctx.message.author),
                   icon_url=user.avatar)
  test1 = mob.title()
  test1 = test1.split()
  test1 = "%20".join(test1)
  embed.set_thumbnail(
      url=
      f"https://github.com/Sniperopo/florr/blob/main/Super/{test1}.png?raw=true"
  )
  await super_channel.send(
      "<@&1182510108706611290> " +
      f"{server.upper()}: Super {str(mob).title()} ({userinp})",
      embed=embed,
      view=view)


async def ultra_report(ctx, mob, server, user, userinp):
  ultra_channel = discord.utils.get(ctx.guild.channels, name="𝗨𝗟𝗧𝗥𝗔-𝗦𝗣𝗔𝗪𝗡𝗦")
  server = str(server)
  embed = discord.Embed(
      title=f"**{server.upper()}: Ultra {str(mob).title()}**",
      description="User input: `{}`".format(ctx.message.content),
      colour=discord.Color.from_rgb(50, 205, 50))
  embed.timestamp = datetime.datetime.now()
  embed.set_author(name="Reported by " + str(ctx.message.author),
                   icon_url=user.avatar)
  test1 = mob.title()
  test1 = test1.split()
  test1 = "%20".join(test1)
  embed.set_thumbnail(
      url=
      f"https://github.com/Sniperopo/florr/blob/main/Ultra/{test1}.png?raw=true"
  )
  await ultra_channel.send(
      "<@&1205179020010979359> " +
      f"{server.upper()}: Ultra {str(mob).title()} ({userinp})",
      embed=embed)


async def test_report(ctx, mob, server, user, userinp):
  test_channel = discord.utils.get(ctx.guild.channels, name="「🤖」𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦")
  server = str(server)
  embed = discord.Embed(
      title=f"**{server.upper()}: Super {str(mob).title()}**",
      description="User input: `{}`".format(ctx.message.content),
      colour=discord.Color.from_rgb(50, 205, 50))
  embed.timestamp = datetime.datetime.now()
  embed.set_author(name="Reported by " + str(ctx.message.author),
                   icon_url=user.avatar)
  test1 = mob.title()
  test1 = test1.split()
  test1 = "%20".join(test1)
  embed.set_thumbnail(
      url=
      f"https://github.com/Sniperopo/florr/blob/main/Super/{test1}.png?raw=true"
  )
  await test_channel.send(
      "<@&1205243455933251704> " +
      f"{server.upper()}: Super {str(mob).title()} ({userinp})",
      embed=embed)

  #test notify 1111010716200210543
  #super notify 1182510108706611290
