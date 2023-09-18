###Bot functions:
###-Wait for someone to summon the bot with "!candulator <amount> <unit> <currency>".
###-When summoned the bot takes <amount> as a number, <unit> as the unit (the unit can be "candles" or "cash") and <currency> that can.
###-If the value of <unit> is "candles" then the bot takes the value of <amount> and calculates how much money those candles cost in the currency specified in <currency>.
###-If the value of <unit> is "cash" then it takes tha value of <amount> and calculates how many candles this amount of money can buy.
###-The default value of <currency> is EUR.
###-TTGC does not follow USD to Currency conversion, so most prices for other currencies are going to be hardcoded. If the currency we are asking for is not hardcoded it will do USD to Currency exchange using api.exchangerate.host
###-The bot replies to the comment that summoned it with "<result> <currency>, <amount> amount of <unit> costs <result> <currency>"

import os
import discord
from discord.ext import commands
import requests

BOT_TOKEN = os.environ.get('BOT_TOKEN')
CANDLE_VALUE = {
    "EUR": 190 / 59.99,
    "USD": 190 / 49.99,
    "CLP": 190 / 55900,
}

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.messages = True
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)

help_text = '''The Candulator Bot can be used to convert between candles and cash.

To use the bot, type `!candulator <amount> <unit> <currency>`. The bot will convert the value of the <amount> from <unit> to <currency> and respond with the result.

- `<amount>`: The amount you want to convert.
- `<unit>`: The unit you want to convert from. The unit can be "candles" or "cash".
- `<currency>` (optional): The currency you want to convert to. The default value is "USD". 

Examples:
- `!candulator 50 candles EUR` will convert 50 candles to EUR.
- `!candulator 100 cash USD` will convert 100 USD to candles.

Note: The exchange rate for some currencies is hardcoded and may not be up to date. For other currencies, the bot will use the exchange rate from api.exchangerate.host and exchange from the price in USD.
'''

# Function to get the final candle value
def get_candle_value(currency):
    if currency in CANDLE_VALUE:
        DEF_CANDLE_VALUE = CANDLE_VALUE[currency]
        print(DEF_CANDLE_VALUE)
    else:
        DEF_CANDLE_VALUE = CANDLE_VALUE["USD"] / get_exchange_rate(currency)
        print(DEF_CANDLE_VALUE)
    return DEF_CANDLE_VALUE

def get_exchange_rate(currency):
    url = f"https://api.exchangerate.host/latest?base=USD&symbols={currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data["rates"][currency]
    else:
        return None

# Function to calculate how much <amount> of candles cost in the specified <currency>
def calculate_cost(amount, currency, DEF_CANDLE_VALUE):
    cost = amount / DEF_CANDLE_VALUE
    return round(cost, 2)

# Function to calculate how many candles can be bought with <amount> of <currency>
def calculate_candles(amount, currency, DEF_CANDLE_VALUE):
    #print("amont: ", amount, ".   currency: ", currency)
    candles = int(amount * DEF_CANDLE_VALUE)
    return candles


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.command()
async def candulator(ctx, amount, unit: str = "candles", currency: str = "USD"):
    # Function to handle the !candulator command
    # Parameters are type-hinted to automatically convert the inputs to the correct type
    # Optional parameter has a default value of "EUR"
    # Input is sanitized to prevent exploits
    if amount == "help":
        response = help_text
    else:
        amount = float(amount)
        amount = abs(amount)# Ensure amount is positive
        unit = unit.lower()# Convert unit to lowercase
        currency = currency.upper()# Convert optional to uppercase
        if unit == "candles":
            cost = calculate_cost(amount, currency, get_candle_value(currency))
            response = f"{cost} {currency}.    {int(amount)} {unit} costs {cost} {currency}"
        elif unit == "cash":
            candles = calculate_candles(amount, currency, get_candle_value(currency))
            response = f"{candles} candles.    {amount} {currency} can buy {candles} candles"
        else:
            response = "Invalid unit. Usage: !candulator <amount> <unit> <currency>"
    await ctx.reply(response)

client.run(BOT_TOKEN)