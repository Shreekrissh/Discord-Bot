import discord
import os
import sys
import asyncio
import google.generativeai as genai
import google.api_core.exceptions
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import pytz

# Load API keys
DISCORD_BOT_TOKEN = ""
GEMINI_API_KEY = ""

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Set up bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Dictionary to store user time zones
user_timezones = {}
# Dictionary to store reminders
reminders = {}

# Restart command (admin only)
@bot.command()
async def restart(ctx):
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ You don't have permission to restart the bot.")
        return
    
    await ctx.send("🔄 Restarting...")
    os.execv(sys.executable, ["python"] + sys.argv)

# Stop command (admin only)
@bot.command()
async def stop(ctx):
    if ctx.author.guild_permissions.administrator:
        await ctx.send("⚠️ Shutting down... Goodbye! 👋")
        await bot.close()
        await asyncio.sleep(1)
        sys.exit(0)
    else:
        await ctx.send("❌ You don't have permission to stop the bot.")

# Test command
@bot.command()
async def hello(ctx):
    await ctx.send("Hello, world! 👋")

# Function to get AI response
def get_gemini_response(user_input):
    try:
        response = model.generate_content(user_input)
        return response.text
    except google.api_core.exceptions.ResourceExhausted:
        return "🚫 I'm out of quota! Please try again later."
    except Exception as e:
        return "⚠️ Oops! Something went wrong. Please try again later."

# Function to safely send long responses
async def send_response(channel, response):
    for i in range(0, len(response), 2000):
        await channel.send(response[i:i+2000])

# Store user AI mode preferences
user_ai_mode = {}

@bot.command()
async def mode(ctx, mode_type: str):
    if mode_type.lower() == "ai":
        user_ai_mode[ctx.author.id] = True
        await ctx.send("🤖 AI Mode Enabled! The bot will respond to all messages.")
    elif mode_type.lower() == "normal":
        user_ai_mode[ctx.author.id] = False
        await ctx.send("💬 Normal Mode Enabled! The bot will only respond to commands.")
    else:
        await ctx.send("⚠️ Invalid mode. Use `!mode ai` or `!mode normal`.")

# Event: When bot is ready
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    check_reminders.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.content.startswith("!"):
        await bot.process_commands(message)
        return
    
    if user_ai_mode.get(message.author.id, False):
        ai_reply = get_gemini_response(message.content)
        await send_response(message.channel, ai_reply)

@bot.command()
async def poll(ctx, question: str, *options):
    if len(options) < 2 or len(options) > 10:
        await ctx.send("Poll must have between 2 and 10 options!")
        return

    embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blue())
    number_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
    poll_text = ""
    for i, option in enumerate(options):
        poll_text += f"{number_emojis[i]} {option}\n"
    embed.add_field(name="Options", value=poll_text, inline=False)
    embed.set_footer(text="React with an emoji to vote!")
    poll_message = await ctx.send(embed=embed)
    for i in range(len(options)):
        await poll_message.add_reaction(number_emojis[i])

# Time Zone Commands
@bot.command()
async def settimezone(ctx, tz: str):
    try:
        pytz.timezone(tz)
        user_timezones[ctx.author.id] = tz
        await ctx.send(f"🌍 Timezone set to `{tz}`.")
    except pytz.UnknownTimeZoneError:
        await ctx.send("⚠️ Invalid timezone. Please use a valid timezone name (e.g., `UTC`, `America/New_York`, `Asia/Kolkata`).")

@bot.command()
async def remind(ctx, time: str, *, message: str):
    user_id = ctx.author.id
    user_tz = user_timezones.get(user_id, "UTC")
    try:
        user_timezone = pytz.timezone(user_tz)
        reminder_time = datetime.strptime(time, "%H:%M").time()
        now = datetime.now(user_timezone)
        reminder_datetime = user_timezone.localize(datetime.combine(now.date(), reminder_time))
        if reminder_datetime < now:
            reminder_datetime += timedelta(days=1)
        reminders[user_id] = (reminder_datetime, message)
        await ctx.send(f"⏰ Reminder set for {reminder_datetime.strftime('%Y-%m-%d %H:%M %Z')} - {message}")
    except ValueError:
        await ctx.send("⚠️ Invalid time format! Use HH:MM (24-hour format).")

@bot.command()
async def delreminder(ctx):
    user_id = ctx.author.id
    if user_id in reminders:
        del reminders[user_id]
        await ctx.send("🗑️ Your reminder has been deleted.")
    else:
        await ctx.send("⚠️ You don't have any active reminders.")

@tasks.loop(seconds=10)
async def check_reminders():
    now = datetime.now(pytz.utc)
    to_remove = []
    for user_id, (reminder_time, message) in reminders.items():
        if now >= reminder_time:
            user = await bot.fetch_user(user_id)
            if user:
                await user.send(f"🔔 Reminder: {message}")
            to_remove.append(user_id)
    for user_id in to_remove:
        del reminders[user_id]

bot.run(DISCORD_BOT_TOKEN)
