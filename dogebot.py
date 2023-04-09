from requests import Request, Session
import json
import smtplib
import time
import robin_stocks.robinhood
import datetime
import yaml
import tweepy


def current_time():
    now = datetime.datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    return dt_string


def tweet(status):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)
    api.update_status(status)


def send_mail(mail_subject, mail_body):
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        msg = f"Subject: {mail_subject}\n\n{mail_body}"
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)


def delay():
    time.sleep(286)


def get_price():
    try:
        url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
        parameters = {'symbol': 'DOGE'}
        headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': API_KEY}
        session = Session()
        session.headers.update(headers)
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
        price_current = (str(data['data']['DOGE']['quote']['USD']['price']))
        return price_current
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None


def main():
    yaml.warnings({'YAMLLoadWarning': False})
    conf = yaml.safe_load(open('info.yml'))
    global EMAIL_ADDRESS, EMAIL_PASSWORD, API_KEY, rhuser, rhpass
    global CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
    EMAIL_ADDRESS = conf['user']['email']
    EMAIL_PASSWORD = conf['user']['emailpassword']
    API_KEY = conf['user']['apikey']
    rhuser = conf['user']['rhusername']
    rhpass = conf['user']['rhpassword']
    CONSUMER_KEY = conf['user']['CONSUMER_KEY']
    CONSUMER_SECRET = conf['user']['CONSUMER_SECRET']
    ACCESS_TOKEN = conf['user']['ACCESS_TOKEN']
    ACCESS_TOKEN_SECRET = conf['user']['ACCESS_TOKEN_SECRET']

    login = robin_stocks.robinhood.login(rhuser, rhpass, expiresIn=86400, by_sms=True)
    current_buy_in = 0.04
    current_high_set_point = 1.0

    while True:
        current_price = get_price()
        if current_price is None:
            print("Failed to fetch price. Retrying in 5 minutes.")
            time.sleep(300)
            continue

        if float(current_price) < current_buy_in:
            mail_subject = "Doge coin has dropped below current low threshold!"
            mail_body = f"Current Price (USD): {current_price} {current_time()}"
            send_mail(mail_subject, mail_body)
            tweet(f"Current Price (USD): {current_price} {current_time()}")
            print(f"Current Price (USD): {current_price} {current_time()}")
            delay()

        elif float(current_price) > current_high_set_point:
            mail_subject = "Doge coin has hit the current high set point check your app."
            mail_body = f"Current Price (USD): {current_price} {current_time()}"
            send_mail(mail_subject, mail_body)
            tweet(f"Current Price (USD): {current_price} {current_time()}")
            print(f"Current Price (USD): {current_price} {current_time()}")
            delay()

        else:
            print(f"Current Price (USD): {current_price} {current_time()}")
            delay()

if __name__ == "__main__":
    main()
