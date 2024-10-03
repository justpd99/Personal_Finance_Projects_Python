import yfinance as yf
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, JobQueue

# Initialize the bot with your Telegram Token
Token = # Replace with your actual token
updater = Updater(Token, use_context=True)
job_queue = JobQueue()
dp = updater.dispatcher
job_queue.set_dispatcher(dp)

# This will hold user triggers in the format: [stock, condition, value, user_id]
l2 = []

# Start command - Greets the user when they start the bot
def start(update, context):
    update.message.reply_text("Hello! Welcome to quicknseupdates. Type /help to know what I am useful for!")

# Help command - Provides instructions on how to use the bot
def help(update, context):
    update.message.reply_text("""
    /start -> Welcome to the channel
    /help -> This message
    To set a trigger, use the format below:
    Trigger stockname condition value
    Example: Trigger tcs g 3199 (greater than 3199)
    Trigger itc l 400 (less than 400)
    """)

# Function to handle trigger creation when the user sends a message
def handle_message(update, context):
    text = str(update.message.text)
    t = text.split()
    uid = update.message.chat_id

    # Check if the message starts with 'trigger' and has correct number of parameters
    if t[0].lower() == "trigger" and len(t) > 3:
        t.pop(0)  # Remove the word 'trigger' from the list
        for i in range(0, len(t), 3):
            # Append stock symbol, condition, target value, and user ID to the list
            l1 = [t[i], t[i + 1], t[i + 2], uid]
            l2.append(l1)
        update.message.reply_text("Subscribed for triggers")
        trigger(context)
    else:
	update.message.reply_text("Please enter a valid response. Type /help to know what I am useful for!")

# Function to check stock price and trigger alerts
def trigger(context):
    while len(l2) > 0:
        for i in l2:
            df1 = yf.Ticker(f"{i[0].upper()}.NS").history(period="1d", interval="1d")
            current_price = df1["Close"][0]  # Fetch the latest closing price

            # Trigger based on greater than condition
            if i[1].lower() == 'g' and current_price > float(i[2]):
                context.bot.send_message(chat_id=i[3], text=f"Triggered for {i[0]} greater than {i[2]}")
                l2.remove(i)

            # Trigger based on less than condition
            elif i[1].lower() == 'l' and current_price < float(i[2]):
                context.bot.send_message(chat_id=i[3], text=f"Triggered for {i[0]} less than {i[2]}")
                l2.remove(i)

# Set up repeating job to check for stock triggers every 5 seconds
job_queue.run_repeating(callback=trigger, interval=5)

# Add command handlers for '/start' and '/help'
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('help', help))

# Add message handler for text messages to set triggers
dp.add_handler(MessageHandler(Filters.text, handle_message))

# Start polling for messages and commands from users
updater.start_polling(5)
job_queue.start()
updater.idle()
