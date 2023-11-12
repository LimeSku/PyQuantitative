# gen des candles et les mets dans un txt pour pas avoir à refetch mes prix...
import pandas as pd
import sys
import datetime
from time import time
from tqdm import tqdm
from requests import Session
from parser import get_args

sys.path.append('../')
sys.path.insert(1, '../app_test/backend/Class/')
sys.path.insert(1, '../app_v2/backend/Class/')

from app_test.backend.Class.cryptocompare import *
from app_v2.backend.web.prices_db import *


EXPORT_DIRECTORY = "exports/"
CORRELATION_EXPORT_DIRECTORY = EXPORT_DIRECTORY+"C_/"

prices_file = EXPORT_DIRECTORY+"prices.csv"

def importWalletInRam(file):
    wallet_csv = pd.read_csv(file)
    return wallet_csv['assets'].values


class Exports:
    _URL_HISTORICAL_DAY = 'https://min-api.cryptocompare.com/data/v2/histoday?fsym={}&tsym=USD&limit={}&e=CCCAGG&tryConversion=false&toTs={}'

    # fetch prices for assets between specified dates
    def exportSQL(self,assets,date_from,date_to):
        date_to = datetime.datetime.fromisoformat(date_to)
        date_from = datetime.datetime.fromisoformat(date_from)

        # For API
        _limit = (date_to-date_from).days
        _toTS = datetime.datetime.timestamp(date_to + datetime.timedelta(1))

        s = Session()
        DB_controller = DB_PRICES_interact()

        URL = self._URL_HISTORICAL_DAY.format({},_limit,_toTS)

        for asset in tqdm(assets):
            # url = self._URL_HISTORICAL_DAY.format(asset,_limit,_toTS)
            url = URL.format(asset)
            response = s.get(url).json()

            if response['Response'] != "Success":
                continue
            candles = response['Data']['Data']
            DB_controller.insertMultiplePrices(asset,candles)
    
    def fetchExportPrices(self,assets,days=365):
        export_file = pd.DataFrame()
        s = Session()

        URL = self._URL_HISTORICAL_DAY.format(days,time())

        for asset in assets:
            data = {}
            url = URL.format(asset)
            response = s.get(url).json()

            if response['Response'] != "Success":
                continue

            candles = response['Data']['Data']
            for candle in candles:
                candle_date = datetime.date.fromtimestamp(candle['time']).isoformat()
                data.update({candle_date:candle['close']})
                export_file.loc[candle_date,asset] = candle['close']
        
        today = datetime.date.today()
        timedelta = datetime.timedelta(days=days)
        export_file.index = pd.date_range((today-timedelta).isoformat(), periods=days+1, freq="D")
        

        location = EXPORT_DIRECTORY+"prices"
        export_file.to_csv(location+".csv")
        export_file.to_excel(location+".xlsx")

        # print(export_file)



if __name__ == "__main__":
    pars = get_args()
    args = pars.parse_args()
    command = args.mode

    wallet = importWalletInRam(EXPORT_DIRECTORY+"assets.csv")
    
    exports = Exports()

    if command == "mix_export":
        _from = "2022-01-16"
        _to = datetime.date.today().isoformat()
        exports.exportSQL(wallet,_from,_to)

    elif command== "sql_export":
        if not args.to:
            _to = datetime.date.today().isoformat()
        else:
            _to = args.to
        
        exports.exportSQL(wallet,args.f,_to)

    elif command == "csv_export":
        exports.fetchExportPrices(wallet)
