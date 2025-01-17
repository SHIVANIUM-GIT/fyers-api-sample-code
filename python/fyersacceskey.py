from datetime import date
from fyers_api import fyersModel
from fyers_api import accessToken
import os
from dotenv import load_dotenv
import time
from fyers_api.Websocket import ws
import datetime as dt
load_dotenv()


client_id = os.getenv('client_id')
secret_key = os.getenv('secret_key')
redirect_uri = os.getenv('redirect_uri')

today = date.today().strftime("%Y-%m-%d")


def get_access_token():
    access = ""
    if not os.path.exists("./authcode"):
        print("Creating authcode directory")
        os.makedirs("./authcode")

    if not os.path.exists(f"authcode/{today}.txt"):
        session = accessToken.SessionModel(client_id=client_id, secret_key=secret_key,
                                           redirect_uri=redirect_uri, response_type="code", grant_type="authorization_code")
        response = session.generate_authcode()
        print("Login Url : ", response)
        auth_code = input("Enter Auth Code : ")
        session.set_token(auth_code)
        access_token = session.generate_token()['access_token']
        with open(f"authcode/{today}.txt", "w") as f:
            f.write(access_token)
    else:
        with open(f"authcode/{today}.txt", "r") as f:
            access = f.read()
    return access


access_token = get_access_token()

fyers = fyersModel.FyersModel(
    client_id=client_id, token=access_token, log_path=os.getcwd())

# print(fyers.get_profile())
# print(fyers.funds())
# # print(fyers.holdings())

# data = {"symbol": "NSE:NIFTYBANK-INDEX", "resolution": "5", "date_format": "1",
#         "range_from": "2023-01-20", "range_to": "2023-01-23", "cont_flag": "1"}

# print(fyers.history(data))


newToken = f"{client_id}:{access_token}"
symbol = ["MCXBULLDEX23JANFUT"]
cws = ws.FyersSocket(access_token=newToken,
                     run_background=False, log_path=os.getcwd())


def on_ticks(msg):
    # print(f"Custom:{msg}")
    script = msg[0]['symbol']
    ltp = msg[0]['ltp']
    open = msg[0]['open']
    high = msg[0]['high_price']
    low = msg[0]['low_price']
    close = msg[0]['close']
    ltt = dt.datetime.fromtimestamp(msg[0]['timestamp'])
    print(
        f"Script:{script} ,LTP:{ltp} ,Open:{open} ,  HIGH:{high}  ,  LOW:{low}, Close:{close} , ltt:{ltt}")
    # time.sleep(60)


cws.websocket_data = on_ticks
cws.subscribe(symbol=symbol, data_type="symbolData")
cws.keep_running()
cws.unsubscribe(symbol=symbol)
