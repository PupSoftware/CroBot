import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta



TOKEN = ''

prefix = './'
intents = discord.Intents.all()



bot = commands.Bot(command_prefix=prefix, help_command=None, intents=intents)



@bot.event
async def on_ready():
    print(f'Bot Is Ready As {bot.user}')
    change_status.start()

@tasks.loop(minutes=1)
async def change_status():
    await bot.change_presence(activity=discord.Game(name="Testing"))
    
    
    
@bot.command(name="ping")
async def ping(ctx):
     await ctx.send(f'Pong! In {round(bot.latency * 1000)}ms')
    
    
@bot.command()
async def kick(ctx, member: discord.Member, *, reason=None):

    await member.kick(reason=reason)

    await ctx.send(f'User {member} has kicked.')

@bot.command()
@commands.has_permissions(ban_members = True)
async def ban(ctx, member : discord.Member, *, reason = None):
    await member.ban(reason = reason)
    
@bot.command()
@commands.has_permissions(administrator = True)
async def unban(ctx, *, member):
    banned_users = await ctx.guild.bans()
    member_name, member_discriminator = member.split("#")

    for ban_entry in banned_users:
        user = ban_entry.user

        if (user.name, user.discriminator) == (member_name, member_discriminator):
            await ctx.guild.unban(user)
            await ctx.send(f'Unbanned {user.mention}')
            return
        
@bot.command(pass_context=True)
@commands.has_permissions(manage_messages=True)
async def purge(ctx, limit: int):
        await ctx.channel.purge(limit=limit)
        await ctx.send('Cleared by {}'.format(ctx.author.mention))
        await ctx.message.delete()
        
@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name='Member')
    await member.add_roles(role)

@bot.command(pass_context=True)
async def ticket(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title='Ticket System',
        description='React 📩 to create a ticket.',
        color=0x00ff00
    )

    embed.set_footer(text="Ticket system")

    msg = await ctx.send(embed=embed)
    await msg.add_reaction("📩")

    def check(reaction, user):
        return user != bot.user and str(reaction.emoji) == '📩'

    while True:
        reaction, user = await bot.wait_for("reaction_add", check=check)
        await msg.remove_reaction(reaction.emoji, user)

        if reaction.emoji == '📩':
            category = discord.utils.get(guild.categories, name="Tickets")
            if not category:
                category = await guild.create_category("Tickets")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                user: discord.PermissionOverwrite(read_messages=True)
            }
            ticket_channel = await guild.create_text_channel(name=f'ticket-{user.name}', overwrites=overwrites, category=category)
            await ticket_channel.send(f'Ticket created by {user.mention}')

            close_embed = discord.Embed(
                title='Close Ticket',
                description='React ❌ to close this ticket.',
                color=0xff0000
            )
            close_message = await ticket_channel.send(embed=close_embed)
            await close_message.add_reaction("❌")

            async def close_ticket():
                def close_check(reaction, user):
                    return user != bot.user and str(reaction.emoji) == '❌' and reaction.message.id == close_message.id

                close_reaction, close_user = await bot.wait_for("reaction_add", check=close_check)
                if close_reaction.emoji == '❌':
                    await ticket_channel.delete()

            bot.loop.create_task(close_ticket())
    
    
bot.run(TOKEN)
