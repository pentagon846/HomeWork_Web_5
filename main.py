import aiohttp
import asyncio
from datetime import datetime, timedelta
import json
import sys


async def fetch_exchange_rates(session, days=1):
    today = datetime.now()
    dates = [(today - timedelta(days=i)).strftime("%d.%m.%Y") for i in range(days)]
    exchange_rates = []
    for date in dates:
        url = f"https://api.privatbank.ua/p24api/exchange_rates?json&date={date}"
        async with session.get(url) as response:
            data = await response.text()
            try:
                json_data = json.loads(data)
                rates = {}
                for rate in json_data.get("exchangeRate", []):
                    if rate["currency"] in ["EUR", "USD"]:
                        currency = rate.get("currency")
                        eur_rate = {"sale": rate.get("saleRateNB", 0), "purchase": rate.get("purchaseRateNB", 0)}
                        rates[currency] = eur_rate
                exchange_rates.append({date: rates})
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON response from API for date {date}.")
                return None
    return exchange_rates


async def main(days=1):
    async with aiohttp.ClientSession() as session:
        exchange_rates = await fetch_exchange_rates(session, days)
        if exchange_rates:
            return exchange_rates
        else:
            print("Error: Invalid response format from API.")
            return []

if __name__ == "__main__":
    days = 1
    if len(sys.argv) > 1:
        try:
            days = int(sys.argv[1])
            if days > 10:
                print("Error: Number of days cannot exceed 10.")
                sys.exit(1)
        except ValueError:
            print("Error: Invalid number of days.")
            sys.exit(1)
    exchange_rates = asyncio.run(main(days))
    print(json.dumps(exchange_rates, ensure_ascii=False, indent=2))
