
import mysql.connector
import sys
from datetime import date

# manage la table price


class DB_PRICES_interact():
    def __init__(self):
        mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="cryptocurrency"
        )
        self.db = mydb
        self.c = mydb.cursor()


    
    def exec_n_commit(self,req,reqD):
        try:
            self.c.execute(req,reqD)
            self.db.commit()
            return True
        except mysql.connector.Error as err:
            print('err in mysql : ',err)
            return False
        except:
            print('Unexpected error: ',sys.exc_info())
            return False
    
    def exec_n_fetch(self,req,reqD=()):
        try:
            self.c.execute(req,reqD)
            tmp_data = self.c.fetchall()
            return tmp_data
        except mysql.connector.Error as err:
            print('error : ',err)
            return False

    def insertPrice(self,crypto_name,date,price):
        req = "INSERT IGNORE INTO daily_prices (name,date,price) VALUES (%s,%s,%s)"
        return self.exec_n_commit(req,(crypto_name,date,price))
    
    def insertMultiplePrices(self,crypto_name,candles):
        req = "INSERT IGNORE INTO daily_prices (name,date,price) VALUES (%s,%s,%s)"
        for candle in candles:
            candle_date = date.fromtimestamp(candle['time']).isoformat()
            self.c.execute(req,(crypto_name,candle_date,candle['close']))
        self.db.commit()

    def getPricesFrom(self,crypto_name,date):
        req = "SELECT date,price FROM daily_prices WHERE name = %s AND date >= %s"
        return self.exec_n_fetch(req,(crypto_name,date))

    def getMultiplePrices(self,crypto_name,_from_date,_to_date):
        req = "SELECT date,price FROM daily_prices WHERE name = %s AND date >= %s AND date <= %s"
        data = self.exec_n_fetch(req,(crypto_name,_from_date,_to_date))
        data_formatted = {}
        for key,price in data:
            data_formatted[key.isoformat()] = price
        return data_formatted

