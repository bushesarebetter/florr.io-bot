import discord
from discord.ext import commands

async def check(ctx, server):
  server = server.lower()
  if server == 'na' or server == 'us':
    await ctx.message.add_reaction("✅")  
    return 'na'
  elif server == 'eu':
    await ctx.message.add_reaction("✅")  
    return 'eu'
  elif server == 'as':
      await ctx.message.add_reaction("✅")  
      return 'as'
  else:
    await ctx.message.add_reaction("❌")
    embed = discord.Embed(
      title="Include a valid server!",
      description="`Valid Server Required`",
      colour=discord.Color.red()
      )
    await ctx.send(embed=embed)
    return 'invalid'
