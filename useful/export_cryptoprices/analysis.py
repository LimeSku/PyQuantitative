import pandas as pd
from scipy.stats import spearmanr
import datetime
from time import time
from argparse import ArgumentParser,ArgumentTypeError
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm
import ML


EXPORT_DIRECTORY = "exports/"
CORRELATION_EXPORT_DIRECTORY = EXPORT_DIRECTORY+"C_/"

prices_file = EXPORT_DIRECTORY+"prices.csv"



### graphicals functions 
# entry : correlation file exported by binary_correlation !
def camembert(period="2022-05-01-2023-01-10"):
    correlation_file = CORRELATION_EXPORT_DIRECTORY+"C_"+period+".csv"
    correlations = pd.read_csv(correlation_file,index_col=0, parse_dates=True)
    pairs = correlations.index
    assets_counter = {pair.split("/")[0]:0 for pair in pairs}
    assets_counter.update({pair.split("/")[1]:0 for pair in pairs})

    for pair in pairs:
        cr = correlations.loc[pair,"Correlation"]
        # print(pair, cr)
        if cr >= 0.8:
            p1,p2 = pair.split("/")
            assets_counter[p1]+=1
            assets_counter[p2]+=1
    # print(assets_counter)
    fig, ax = plt.subplots()
    ax.pie(assets_counter.values(), labels=assets_counter.keys(), startangle=90)
    ax.axis('equal')
    plt.title("nb de corrélations pour une crypto donnée avec les autres")
    plt.show()





def importWalletInRam(db):
    # wallet_csv = pd.read_csv("assets.csv")
    return pd.read_csv(db,index_col=0, parse_dates=True).columns

def getMultipleCryptoPrice(name,_from,_to):
    df = pd.read_csv(prices_file,index_col=0, parse_dates=True)
    return df.loc[_from:_to,name]

def getCryptoPrice(name,date):
    df = pd.read_csv(prices_file,index_col=0, parse_dates=True)
    return df.loc[date,name]



# take isoformat and add it n days
def incrementDays(date,days):
    return (datetime.date.fromisoformat(date)+datetime.timedelta(days=days)).isoformat()

def decrementDays(date,days):
    return (datetime.date.fromisoformat(date)-datetime.timedelta(days=days)).isoformat()



# calcule la correlation de spearman sur une période donnée
# args : 
# a1, a2 -> str
# _from, _to -> date isoformat (YYYY-MM-DD)
def correlation(a1,a2,_from,_to,db=prices_file):
    wallet = pd.read_csv(db,index_col=0, parse_dates=True)
    a1_prices = wallet.loc[_from:_to,a1]
    a2_prices = wallet.loc[_from:_to,a2]
    return spearmanr(a1_prices,a2_prices)


# same as correlation, but with a padding between days
def delayed_correlation(a1,a2,_fromA1,_fromA2,days,db=prices_file):
    wallet = pd.read_csv(db,index_col=0, parse_dates=True)
    delta = datetime.timedelta(days=days)
    _toA1 = (delta+datetime.date.fromisoformat(_fromA1)).isoformat()
    _toA2 = (delta+datetime.date.fromisoformat(_fromA2)).isoformat()
    a1_prices = wallet.loc[_fromA1:_toA1,a1]
    a2_prices = wallet.loc[_fromA2:_toA2,a2]
    print(a2_prices)
    return spearmanr(a1_prices,a2_prices)




def binary_correlation(assets,_from,_to):
    correlations_export = pd.DataFrame()
    n_assets = len(assets)
    for i in range(n_assets):
        for j in range(i):
            C = correlation(assets[i],assets[j],_from,_to)
            correlations_export.loc[assets[i]+"/"+assets[j],"Correlation"] = C[0]
            correlations_export.loc[assets[i]+"/"+assets[j],"PValue"] = C[1]
            # correlations_export.loc[assets[j]+"/"+assets[i],"Correlation"] = C[0]
            # correlations_export.loc[assets[j]+"/"+assets[i],"PValue"] = C[1]
        # print(correlations_export)
    
    correlations_export = correlations_export.sort_values(by=['Correlation'],ascending=False)
    location = CORRELATION_EXPORT_DIRECTORY+"C_"+_from+"-"+_to
    correlations_export.to_excel(location+".xlsx")
    correlations_export.to_csv(location+".csv")



def binary_correlation_heatmap(assets,_from,_to):
    correlations_export = pd.DataFrame(index=assets)
    n_assets = len(assets)
    print(assets)
    for i in range(n_assets):
        for j in range(i):
            C = correlation(assets[i],assets[j],_from,_to)
            correlations_export.loc[assets[i],assets[j]] = C[0]
            correlations_export.loc[assets[j],assets[i]] = C[0]
            correlations_export.loc[assets[i],assets[i]] = 1

            # correlations_export.loc[assets[i]+"/"+assets[j],"PValue"] = C[1]
            # correlations_export.loc[assets[j]+"/"+assets[i],"Correlation"] = C[0]
            # correlations_export.loc[assets[j]+"/"+assets[i],"PValue"] = C[1]
        # print(correlations_export)
    correlations_export.loc[assets[0],assets[0]] = 1
    print(correlations_export)
    # correlations_export = correlations_export.sort_values(by=['Correlation'],ascending=False)
    location = CORRELATION_EXPORT_DIRECTORY+"HM\\C_"+_from+"-"+_to
    correlations_export.to_excel(location+".xlsx")
    correlations_export.to_csv(location+".csv")


def limit_padding_type(x):
    x = int(x)
    if x < 4:
        raise ArgumentTypeError("Minimum limit is 4")
    return x


# délayer les corrélations...
if __name__ == "__main__":
    parser = ArgumentParser(description='Wallet Manager')

    subparsers = parser.add_subparsers(dest='mode')
    subparsers.required = True  # required since 3.7
    
    # parser for binary correlation
    parser_binCor = subparsers.add_parser('cor')
    parser_binCor.add_argument('-a',"--assets", type=str, default=[prices_file],
        help="locate assets file")

    parser_binCor.add_argument('-f',"--from", type=str, default="2022-05-01",
        help="from period")

    parser_binCor.add_argument('-t',"--to", type=str, default="2023-01-10",
        help="to period")
    
    #search regression = SR
    parser_SR = subparsers.add_parser('SR')
    parser_SR.add_argument('-b',"--backdays",type=int,default=20,
        help="")
    parser_SR.add_argument('-l',"--limit",type=limit_padding_type,default=4,
        help="")


    parser_chart = subparsers.add_parser('chart')
    parser_chart.add_argument('-c',"--chart-type",type=int,default=1,
    help="Choose chart type. 1 = camembert ; 2 = HM correlations")
    
    args = parser.parse_args()


    command = args.mode
    if command == "cor":
        assets = importWalletInRam(prices_file)
        # print(correlation(assets[0],assets[1],"2022-05-01","2023-01-10"))
        # print(delayed_correlation(assets[0],assets[1],"2022-05-01","2022-05-11",10))
        # t1 = time()
        binary_correlation(assets,"2022-05-01","2023-01-10")
        binary_correlation_heatmap(assets,"2022-05-01","2023-01-10")

        # print(time()-t1)
    elif command == "chart":
        if args.chart_type == 1:
            camembert(period="2022-05-01-2023-01-10")
        elif args.chart_type == 2:
            endpoint = CORRELATION_EXPORT_DIRECTORY+"HM\\"+"C_2022-05-01-2023-01-10.csv"
            t1 = time()
            df_correlation = pd.read_csv(endpoint,index_col=0)
            print(time()-t1)
            sns.heatmap(df_correlation,annot=True,cmap='viridis')
            plt.show()
        elif args.chart_type == 3:
            endpoint = CORRELATION_EXPORT_DIRECTORY+"HM\\"+"C_2022-05-01-2023-01-10.csv"
            df_correlation = pd.read_csv(endpoint,index_col=0)



    # cherche une regression polynomiale
    elif command == "SR":
        df_correlation = pd.read_csv(CORRELATION_EXPORT_DIRECTORY+"C_2022-05-01-2023-01-10.csv",index_col=0)
        candidats = df_correlation.loc[df_correlation['Correlation'] >=0.8].index
        backdays = args.backdays-1
        
        # End_date = date d'aujourd'hui puis on recule de "backdays" jours pour avoir la plage max
        # puis on avance dans le FOR pour étudier des plages + en + petites

        end_date = datetime.date.today().isoformat()
        start_date = decrementDays(end_date,backdays)
        limit = args.limit # pour ne pas avoir de pb sur la longueur de l'échantillon
        limit_date = decrementDays(end_date,limit)
        print("Searching in candidats from {} to {} ({} days)".format(start_date,end_date,backdays+1))

        for pair in tqdm(candidats):
            a1,a2 = pair.split("/")
            p1 = getMultipleCryptoPrice(a1,start_date,end_date)
            p2 = getMultipleCryptoPrice(a2,start_date,end_date)

            start_date_tmp = start_date
            found_reg = False
            while start_date_tmp != limit_date and not found_reg:
                # print(pair, ML.searchModel(p1,p2))
                # degree = ML.bestDeg(p1,p2)
                # if degree :

                # print(pair,start_date_tmp," -> ",end_date)
                
                # ML.skSearch(p1,p2,pair,degree)
                plot = ML.ridgeRegression(p1,p2)
                plot.title(pair)
                plot.show()
                found_reg = True


                start_date_tmp = incrementDays(start_date_tmp,1)
                p1 = p1[1:]
                p2 = p2[1:]
                



        
    