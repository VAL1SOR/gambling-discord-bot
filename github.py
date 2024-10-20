import discord
from discord import app_commands
from discord.ext import commands
import random
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy import Column, Integer, String, BigInteger
import sqlalchemy

SQLALCHEMY_DATABASE_URL = f'postgresql://database_username:database_password@database_ip:database_port/database_name'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

Base = sqlalchemy.orm.declarative_base()

class Balance(Base):
  __tablename__ = 'balance'

  uid = Column(BigInteger, primary_key = True, nullable = False)
  balance = Column(BigInteger, nullable = False)

Base.metadata.create_all(bind = engine)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

client = commands.Bot(command_prefix="/", intents=intents)

@client.event
async def on_ready():
  print(client.user)
  await client.change_presence(activity=discord.Game(name="GAMBLE!!!"))
  try:
    s = await client.tree.sync()
    print(f"Synced {len(s)} commands")
  except Exception as e:
    print(e)

@client.tree.command(name="start")
@app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def start(interaction: discord.Interaction):
  embed = discord.Embed(colour = discord.Colour.yellow(), title = f"You are ready to go gambling!!!")
  embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
  user = int(interaction.user.id)
  with SessionLocal() as db:
    user_balance = db.query(Balance).filter(Balance.uid == user).first()
    if not user_balance:
      new_entry = Balance(uid = user, balance = 100)
      db.add(new_entry)
      db.commit()
      user_balance = db.query(Balance).filter(Balance.uid == user).first()
  embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
  await interaction.response.send_message(embed = embed)

@client.tree.command(name="pity")
@app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def pity(interaction: discord.Interaction):
  user = interaction.user
  with SessionLocal() as db:
    user_balance = db.query(Balance).filter(Balance.uid == int(user.id)).first()
    if (not user_balance):
      embed = discord.Embed(colour = discord.Colour.yellow(), title = "You do not have a wallet. Do `/start` to make one.")
      embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
      await interaction.response.send_message(embed = embed)
      return
    if (user_balance.balance <= 0):
      db.query(Balance).filter(Balance.uid == user.id).update({'balance': 100}, synchronize_session = False)
      db.commit()
      user_balance = db.query(Balance).filter(Balance.uid == int(user.id)).first()
      embed = discord.Embed(colour = discord.Colour.yellow(), title = f"Since i pity {user.name} i will give him a balance of {user_balance.balance} coins", description = str(user_balance.balance) + " coins")
      embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
    else:
      embed = discord.Embed(colour = discord.Colour.yellow(), title = f"I don't need to pity {user.name}, he has a balance of {user_balance.balance} coins. He is basically rich.", description = str(user_balance.balance) + " coins")
      embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
  await interaction.response.send_message(embed = embed)

@client.tree.command(name="balance")
@app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
async def balance(interaction: discord.Interaction, user: discord.Member = None):
  with SessionLocal() as db:
    if not user:
      user = interaction.user
    elif (not db.query(Balance).filter(Balance.uid == int(user.id)).first()):
      new_entry = Balance(uid = int(user.id), balance = 100)
      db.add(new_entry)
      db.commit()
    user_balance = db.query(Balance).filter(Balance.uid == int(user.id)).first()
    if not user_balance:
      embed = discord.Embed(colour = discord.Colour.yellow(), title = "You do not have a wallet. Do `/start` to make one.")
      embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
      await interaction.response.send_message(embed = embed)
      return
    embed = discord.Embed(colour = discord.Colour.yellow(), title = f"{user.name}'s balance:", description = str(user_balance.balance) + " coins")
    embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
  await interaction.response.send_message(embed = embed)

@client.tree.command(name="donate")
@app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
@app_commands.describe(to = "The user you want to donate to.", amount = "Amount to donate.")
async def donate(interaction: discord.Interaction, to: discord.Member, amount: int):

  donator = interaction.user.id
  donatee = to.id

  if (donator == donatee):
    embed = discord.Embed(colour=discord.Colour.red(), title="You can't donate to yourself.")
    await interaction.response.send_message(embed=embed)
    return
  if amount <= 0:
    embed = discord.Embed(colour=discord.Colour.red(), title="Invalid amount.", description="Please enter a positive amount to donate.")
    await interaction.response.send_message(embed=embed)
    return

  with SessionLocal() as db:
    donator_balance = db.query(Balance).filter(Balance.uid == donator).first()
    donatee_balance = db.query(Balance).filter(Balance.uid == donatee).first()

    if not donator_balance:
      embed = discord.Embed(colour = discord.Colour.yellow(), title = "You are not ready to donate. Do `/start` to ready up.")
      embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
      await interaction.response.send_message(embed = embed)
      return
    
    if donator_balance.balance < amount:
      embed = discord.Embed(colour=discord.Colour.red(), title="Insufficient balance.", description=f"You only have {donator_balance.balance} coins.")
      await interaction.response.send_message(embed=embed)
      return
    
    if not donatee_balance:
      new_entry = Balance(uid = int(donatee), balance = 100)
      db.add(new_entry)
      db.commit()
      donatee_balance = db.query(Balance).filter(Balance.uid == donatee).first()

    db.query(Balance).filter(Balance.uid == donator).update({'balance': int(int(donator_balance.balance) - int(amount))}, synchronize_session = False)
    db.query(Balance).filter(Balance.uid == donatee).update({'balance': int(int(donatee_balance.balance) + int(amount))}, synchronize_session = False)
    db.commit()
    donator_balance = db.query(Balance).filter(Balance.uid == donator).first()
    donatee_balance = db.query(Balance).filter(Balance.uid == donatee).first()
    embed = discord.Embed(colour = discord.Colour.yellow(), title = f"{interaction.user} donated {str(amount)} coins to {to}")
    embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
  await interaction.response.send_message(embed = embed)

@client.tree.command(name="diceroll")
@app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
@app_commands.describe(d = "Number of faces.")
async def diceroll(interaction: discord.Interaction, d: int = 6):
  embed = discord.Embed(colour = discord.Colour.yellow(), title = f"You rolled a {random.randint(1, d)}")
  embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
  embed.set_footer(text = "D" + str(d))
  await interaction.response.send_message(embed = embed)

@client.tree.command(name="coinflip")
@app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
@app_commands.choices(face = [app_commands.Choice(name="heads", value="heads"), app_commands.Choice(name="tails", value="tails"),])
@app_commands.describe(bet = "How much do you bet.", face = "What face are you betting on.")
async def coinflip(interaction: discord.Interaction, bet: int, face: app_commands.Choice[str]):
  user = int(interaction.user.id)
  with SessionLocal() as db:
    user_balance = db.query(Balance).filter(Balance.uid == user).first()
    if not user_balance:
      embed = discord.Embed(colour = discord.Colour.yellow(), title = "You are not ready to gamble. Do `/start` to ready up.")
      embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
    else:
      if ((bet > 0) and (bet <= int(user_balance.balance))):
        db.query(Balance).filter(Balance.uid == user).update({'balance': int(int(user_balance.balance) - int(bet))}, synchronize_session = False)
        db.commit()
        user_balance = db.query(Balance).filter(Balance.uid == user).first()
        side = random.choice(["heads", "tails"])
        if (face.value == side):
          db.query(Balance).filter(Balance.uid == user).update({'balance': int(int(user_balance.balance) + int(int(bet) * 2))}, synchronize_session = False)
          db.commit()
          embed = discord.Embed(colour = discord.Colour.yellow(), title = side, description = f"You won {bet}")
          user_balance = db.query(Balance).filter(Balance.uid == user).first()
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
        else:
          embed = discord.Embed(colour = discord.Colour.yellow(), title = side, description = f"You lost {bet}")
          embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
      else:
          embed = discord.Embed(colour = discord.Colour.yellow(), title = "Incorrect use of command.")
          embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
  await interaction.response.send_message(embed = embed)

@client.tree.command(name="dice")
@app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
@app_commands.describe(bet = "How much do you bet.")
async def dice(interaction: discord.Interaction, bet: int):
  user = int(interaction.user.id)
  with SessionLocal() as db:
    user_balance = db.query(Balance).filter(Balance.uid == user).first()
    if not user_balance:
      embed = discord.Embed(colour = discord.Colour.yellow(), title = "You are not ready to gamble. Do `/start` to ready up.")
      embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
    else:
      if ((bet > 0) and (bet <= int(user_balance.balance))):
        db.query(Balance).filter(Balance.uid == user).update({'balance': int(int(user_balance.balance) - int(bet))}, synchronize_session = False)
        db.commit()
        user_balance = db.query(Balance).filter(Balance.uid == user).first()
        num = random.randint(1, 6)
        if (num == 6):
          db.query(Balance).filter(Balance.uid == user).update({'balance': int(int(user_balance.balance) + int(int(bet) * 6))}, synchronize_session = False)
          db.commit()
          embed = discord.Embed(colour = discord.Colour.yellow(), title = str(num), description = f"You won {bet * 5} coins")
          user_balance = db.query(Balance).filter(Balance.uid == user).first()
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
        else:
          embed = discord.Embed(colour = discord.Colour.yellow(), title = str(num), description = f"You lost {bet} coins")
          embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
      else:
          embed = discord.Embed(colour = discord.Colour.yellow(), title = "Incorrect use of command.")
          embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
  await interaction.response.send_message(embed = embed)

@client.tree.command(name="shell")
@app_commands.allowed_installs(guilds = True, users = True)
@app_commands.allowed_contexts(guilds = True, dms = True, private_channels = True)
@app_commands.choices(cup = [app_commands.Choice(name="first", value="first"), app_commands.Choice(name="second", value="second"), app_commands.Choice(name="last", value="last"),])
@app_commands.describe(bet = "How much do you bet.", cup = "What cup do you bet on.")
async def shell(interaction: discord.Interaction, cup: app_commands.Choice[str], bet: int):
  user = int(interaction.user.id)
  with SessionLocal() as db:
    user_balance = db.query(Balance).filter(Balance.uid == user).first()
    if not user_balance:
      embed = discord.Embed(colour = discord.Colour.yellow(), title = "You are not ready to gamble. Do `/start` to ready up.")
      embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
    else:
      if ((bet > 0) and (bet <= int(user_balance.balance))):
        db.query(Balance).filter(Balance.uid == user).update({'balance': int(int(user_balance.balance) - int(bet))}, synchronize_session = False)
        db.commit()
        user_balance = db.query(Balance).filter(Balance.uid == user).first()
        num = random.choice(["first", "second", "last"])
        if (num == cup.value):
          db.query(Balance).filter(Balance.uid == user).update({'balance': int(int(user_balance.balance) + int(int(bet) * 2))}, synchronize_session = False)
          db.commit()
          embed = discord.Embed(colour = discord.Colour.yellow(), title = f"The ball was in the {str(num)} cup", description = f"You won {bet} coins")
          user_balance = db.query(Balance).filter(Balance.uid == user).first()
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
        else:
          embed = discord.Embed(colour = discord.Colour.yellow(), title = f"The ball was in the {str(num)} cup", description = f"You lost {bet} coins")
          embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
      else:
          embed = discord.Embed(colour = discord.Colour.yellow(), title = "Incorrect use of command.")
          embed.set_author(name = "GDGB", url = "https://discord.com/oauth2/authorize?client_id=1268172241703534652", icon_url = "https://lb93production2.wordpress.com/wp-content/uploads/2015/07/mario5.png")
          embed.set_footer(text = f"You have a balance of {str(user_balance.balance)} coins")
  await interaction.response.send_message(embed = embed)

client.run('discord_bot_token')