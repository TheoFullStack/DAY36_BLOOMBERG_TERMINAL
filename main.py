import requests
import os
import datetime as dt

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
API_KEY1 = os.environ.get("API_KEY")
API_KEY2 = os.environ.get("NEWS_API_KEY")

URL= f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&outputsize=compact&apikey={API_KEY1}"

capital_return = 0

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
raw_today = dt.datetime.now()
#use this as today
today = raw_today.strftime('%Y-%m-%d')
today_datetime = dt.datetime.strptime(today, '%Y-%m-%d')
today_name = today_datetime.strftime('%A')
print(today_name)
#use this as today


#use this as yesterday
yesterday_raw = today_datetime - dt.timedelta(days=1)
yesterday = yesterday_raw.strftime('%Y-%m-%d')
#use this as yesterday
print(f'Yesterday:',yesterday)
print(f'today: ',today)


response = requests.get(url=URL)
response.raise_for_status()
stock_data = response.json()
today_close = 0
yesterday_close = 0
did_close = True


def return_calc():
    global stock_data,today,yesterday,today_datetime,yesterday_raw,capital_return,today_close,yesterday_close,did_close
    if today in stock_data['Time Series (Daily)']:
        today_close = float(stock_data['Time Series (Daily)'][today]['4. close'])
        if today_name == "Monday":
            yesterday_raw = today_datetime - dt.timedelta(days=3)
            yesterday = yesterday_raw.strftime('%Y-%m-%d')
        else:
            yesterday_raw = today_datetime - dt.timedelta(days=1)
            yesterday = yesterday_raw.strftime('%Y-%m-%d')
        yesterday_close = float(stock_data['Time Series (Daily)'][yesterday]['4. close'])
        capital_return = round(((today_close - yesterday_close) / yesterday_close) * 100, ndigits=2)
    elif today_name == "Saturday":
        today = today_datetime - dt.timedelta(days=1)
        today_close = float(stock_data['Time Series (Daily)'][today]['4. close'])
        yesterday_raw = today_datetime - dt.timedelta(days=2)
        yesterday = yesterday_raw.strftime('%Y-%m-%d')
        yesterday_close = float(stock_data['Time Series (Daily)'][yesterday]['4. close'])
        capital_return = round(((today_close - yesterday_close) / yesterday_close) * 100, ndigits=2)
    elif today_name == "Sunday":
        today = today_datetime - dt.timedelta(days=2)
        today_close = float(stock_data['Time Series (Daily)'][today]['4. close'])
        yesterday_raw = today_datetime - dt.timedelta(days=3)
        yesterday = yesterday_raw.strftime('%Y-%m-%d')
        yesterday_close = float(stock_data['Time Series (Daily)'][yesterday]['4. close'])
        capital_return = round(((today_close - yesterday_close) / yesterday_close) * 100, ndigits=2)
    else:
        print("Something went wrong with today if statement. Closure might have not happened yet.")
        did_close = False
        capital_return = 0
    return capital_return



## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
URL2= f"https://newsapi.org/v2/everything?q={COMPANY_NAME}&from={yesterday}&sortBy=popularity&language=en&apiKey={API_KEY2}"
response2 = requests.get(url=URL2)
response2.raise_for_status()

news_data = response2.json()






# Initialize lists to store titles and brief texts
titles = []
brief_texts = []

# Extract the first three titles and brief texts
for article in news_data['articles'][:3]:
    titles.append(article['title'])
    brief_texts.append(article['description'])

# Print the first three titles and brief texts
for title, brief_text in zip(titles, brief_texts):
    print("Title:", title)
    print("Brief text:", brief_text)
    print()  # Empty line for separation




## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number.
sign: str
sign = "down"


from twilio.rest import Client
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)


sign = None

if capital_return < -0.05:
    sign = "Down 🔻"
    message = client.messages \
        .create(
            body=f"TSLA: {capital_return} {sign}\nHeadline: {title}\nBrief: {brief_text}",
            from_='+15315414858',
            to=os.environ['MY_PHONE_NUMBER'],
        )
elif capital_return > 0.10:
    sign = "Up 🔺"
    message = client.messages \
                .create(
                     body=f"TSLA: {capital_return} {sign}\nHeadline: {title}\nBrief: {brief_text}",
                     from_='+15315414858',
                     to= os.environ['MY_PHONE_NUMBER']
                 )
else:
    sign = "N/A"
    message = client.messages \
                .create(
                     body=f"Markets did not close yet.:\nTSLA: {capital_return} {sign}\nHeadline: {title}\nBrief: {brief_text}",
                     from_='+15315414858',
                     to= os.environ['MY_PHONE_NUMBER']
                 )

print(message.sid)
print(os.environ['MY_PHONE_NUMBER'])

#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

