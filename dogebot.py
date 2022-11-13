from requests import Request, Session
import json
import smtplib
import time
import robin_stocks.robinhood
import datetime
import yaml


def CurrentTime():
    now = datetime.datetime.now()
    dt_string = now.strftime("%m/%d/%Y %H:%M:%S")
    return dt_string
def sendMail(mailSubject,mailBody):
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            subject = mailSubject
            body = mailBody
            msg = f"Subject: {subject}\n\n{body}"
            smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)
def delay():
    time.sleep(286)
def getPrice():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest' #coin market url
    parameters = {'symbol': 'DOGE'}
    headers = {'Accepts': 'application/json', 'X-CMC_PRO_API_KEY': API_KEY}
    session = Session()
    session.headers.update(headers)
    response = session.get(url, params=parameters)
    data = json.loads(response.text)
    priceCurrent = (str(data['data']['DOGE']['quote']['USD']['price']))
    #print ('24h Volume (USD):    ' + str(data['data']['DOGE']['quote']['USD']['volume_24h']))
    #print ('Market Cap (USD):    ' + str(data['data']['DOGE']['quote']['USD']['market_cap']))
    return priceCurrent
def buy(amount): #number of doge coin's to buy
    robin_stocks.orders.order_buy_crypto_by_quantity('DOGE', float(amount), timeInForce='gtc')
def sell(amount):
    robin_stocks.orders.order_sell_crypto_by_quantity('DOGE', float(amount), priceType='mark_price', timeInForce='gtc')
def cancel(): #cancel all crypto orders
    robin_stocks.orders.cancel_all_crypto_orders()
def dollarToDoge(dollar, currentPrice):
    conversion = doller / currentPrice
    return conversion
def dogeToDollar(doge, currentPrice):
    conversion = doge * currentPrice
    return conversion

yaml.warnings({'YAMLLoadWarning': False})
conf = yaml.safe_load(open('info.yml'))
EMAIL_ADDRESS = conf['user']['email']
EMAIL_PASSWORD = conf['user']['emailpassword']
API_KEY = conf['user']['apikey']
rhuser = conf['user']['rhusername']
rhpass = conf['user']['rhpassword']

login = robin_stocks.robinhood.login(rhuser, rhpass, expiresIn=86400, by_sms=True) #robinhood login
currentBuyIn = 0.04 #price of doge on last pruchase
currentHighSetPoint = 1.0

while True:
    try:
        currentPrice = getPrice()
    except Exception as e:
        print(e)
    if float(currentPrice) < currentBuyIn:
        mailSubject = "Doge coin has dropped below current low threshold!"
        mailBody = ('Current Price (USD): ' + str(currentPrice) + ' ' + str(CurrentTime()))
        sendMail(mailSubject,mailBody)
        print('Current Price (USD): ' + str(currentPrice) + ' ' + str(CurrentTime()))
        delay()
    elif float(currentPrice) > currentHighSetPoint:
        mailSubject = "Doge coin has hit the current high set point check your app."
        mailBody = ('Current Price (USD): ' + str(currentPrice) + ' ' + str(CurrentTime()))
        sendMail(mailSubject,mailBody)
        print('Current Price (USD): ' + str(currentPrice) + ' ' + str(CurrentTime()))
        delay()
    else:
        print('Current Price (USD): ' + str(currentPrice) + ' ' + str(CurrentTime()))
        delay()
