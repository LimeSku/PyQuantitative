from sklearn.metrics import r2_score
from sklearn.linear_model import LinearRegression,RidgeCV,Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures
from sklearn import linear_model
import numpy
import seaborn as sns
import warnings


# recherche un degré n qui valide une régression polynomiale sur deux actifs
def searchModel(x,y):
    limit = int(len(x)*0.8)
    train_x,train_y = x[:limit],y[:limit]
    test_x,test_y = x[limit:],y[limit:]
    ltotal = 0

    with warnings.catch_warnings():
        warnings.filterwarnings('error')
        for i in range(1,12):
            try:
                mymodel = numpy.poly1d(numpy.polyfit(train_x, train_y, i))
            except numpy.RankWarning:
                continue
            r2_train = r2_score(train_y, mymodel(train_x))
            r2_test = r2_score(test_y, mymodel(test_x))
            total = r2_train + r2_test
            if total > ltotal :
                degree = i
                ltotal = total
    if ltotal > 1.8:
        return degree
    return None



def bestDeg(X,Y):
    #train,verif
    l = int(len(X)*0.8)
    #set de base, de training et de vérification
    _x = numpy.array(X).reshape((-1, 1))
    _y = numpy.array(Y).reshape((-1, 1))

    t_X = _x[:l]
    t_y = _y[:l]
    v_x = _x[l:]
    v_y = _y[l:]

    train = [t_X,t_y]
    verif = [v_x,v_y]

    degree = 0
    ltotal = 0
    with warnings.catch_warnings() as error:
        for i in range(1,12):
            reg=make_pipeline(PolynomialFeatures(i),LinearRegression())
            reg.fit(train[0],train[1])
            r2_train = reg.score(train[0],train[1])
            r2_test = reg.score(verif[0],verif[1])
            total = r2_train + r2_test
            if total > ltotal :
                degree = i
                ltotal = total
            # print(ltotal)
    return degree

def skSearch(x,y,pair,degree):
    l = int(len(x)*0.8)
    #set de base, de training et de vérification
    _x = numpy.array(x).reshape((-1, 1))
    _y = numpy.array(y).reshape((-1, 1))
    t_X = _x[:l]
    t_y = _y[:l]
    v_x = _x[l:]
    v_y = _y[l:]

    # degree=bestDeg([t_X,t_y],[v_x,v_y])
    reg=make_pipeline(PolynomialFeatures(degree),LinearRegression())
    reg.fit(t_X,t_y)
    if(reg.score(t_X,t_y)>0.9 and reg.score(v_x,v_y) >0.9):
        # print(reg,reg.score(t_X,t_y),reg.coef_)
        myline = numpy.linspace(min(x), max(x), len(x)).reshape((-1,1))
        plt.plot(myline,reg.predict(myline))
        plt.title(pair+" "+str(len(x))+" Days")
        plt.scatter(_x,_y,color="coral")
        plt.show()





# faire une regression ridge vs lasso pour voir




# Ridge Regression without standardization
def ridgeRegression(X,y):
    y_ = y
    X = numpy.array(X).reshape((-1, 1))
    y = numpy.array(y).reshape((-1, 1))
    X_train,X_test, y_train,y_test = train_test_split(X,y, test_size=0.25,random_state=43)
    r_alphas = 1

    # calculer le score et cross validation
    ridge_model = Ridge(alpha=r_alphas)
    ridge_model = ridge_model.fit(X_train,y_train)
    y_pred = ridge_model.predict(X_test)
    # print("r2 score test vs pred for y axis : ",r2_score(y_test,y_pred))
    
    # sns.distplot(y_test-y_pred)
    # plt.plot()
    myline = numpy.linspace(min(X), max(X), len(X)).reshape((-1,1))

    plt.scatter(X_train,y_train,label="Training",s=5)
    plt.scatter(X_test,y_test,label="Test",s=5)
    # errors = [y_[i] + ridge_model.predict(myline)[i] for i in range(len(y_))]
    plt.plot(myline,ridge_model.predict(myline),label="Prediction",color="green")

    # plt.errorbar(myline, ridge_model.predict(myline), yerr = errors,
    # fmt = 'none', capsize = 10, ecolor = 'green', elinewidth = 2, capthick = 8)

    # z = [elt[0] for elt in myline]
    # y1 = [elt[0] for elt in (ridge_model.predict(myline)*0.95)]
    # y2 = [elt[0] for elt in (ridge_model.predict(myline)*1.05)]

    # plt.fill_between(z,y1,y2,color="green")
    # plt.scatter(X,y,color="coral",s=4)

    return plt
    # return y_pred


def polynomialRegression(X,y):
    X = numpy.array(X).reshape((-1, 1))
    y = numpy.array(y).reshape((-1, 1))
    