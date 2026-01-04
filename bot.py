import os
import discord
from discord.ext import commands
from discord import app_commands

# ==== CONFIG (READ FROM RAILWAY SECRETS) ====
TOKEN = os.getenv("TOKEN")                         # Set in Railway
CHECKIN_CHANNEL_ID = int(os.getenv("CHECKIN_CHANNEL_ID"))  # Set in Railway


ALLOWED_KEYWORDS = [
    # single-word triggers
    "strayer",
    "student",
    "professor",
    "professor ford",
    "ford",
    "meeting",

    # phrases
    "came from the professors meeting",
    "im a strayer student",
    "i'm a strayer student",
    "i came from the meeting",
    "i came from strayer",
    "strayer student"
]

# ==== INTENTS ====
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


# ================= BOT READY =================
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")


# ================= AUTO VERIFICATION =================
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # Only process messages in the check-in channel
    if message.channel.id == CHECKIN_CHANNEL_ID:
        text = message.content.lower()
        print("Check-in message:", text)

        if any(keyword in text for keyword in ALLOWED_KEYWORDS):

            role = discord.utils.get(message.guild.roles, name="Student")

            if not role:
                return await message.channel.send(
                    "I couldn't find the Student role — let an admin know."
                )

            # already verified?
            if role in message.author.roles:
                return await message.channel.send(
                    f"You're already verified, {message.author.mention}! 🎉"
                )

            try:
                await message.author.add_roles(role)
                await message.channel.send(
                    f"You're verified, {message.author.mention}! 🎉 Welcome!"
                )
            except discord.Forbidden:
                await message.channel.send(
                    "I tried to give you the Student role but I don't have permission. "
                    "Ask an admin to move my role ABOVE the Student role."
                )

        else:
            await message.channel.send(
                "Hi there nerd! Quick question, how did you hear about this server?"
            )

    await bot.process_commands(message)


# ================= MANUAL VERIFY COMMAND =================
@bot.tree.command(
    name="verify",
    description="Manually verify a member and give them student access."
)
@app_commands.checks.has_permissions(manage_roles=True)
async def verify(interaction: discord.Interaction, member: discord.Member):

    role = discord.utils.get(interaction.guild.roles, name="Student")

    if not role:
        return await interaction.response.send_message(
            "I couldn't find the Student role.", ephemeral=True
        )

    await member.add_roles(role)
    await interaction.response.send_message(
        f"{member.mention} has been manually verified and given access. ✅"
    )


bot.run(TOKEN)
