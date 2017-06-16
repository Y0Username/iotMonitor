import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from sklearn import linear_model

url="/Users/Yathish/Desktop/UCI/TIPPERS/learn/mlearn/javaCity1.data"
data = pd.read_csv(url, sep=",", header = None)
data.columns = ["type", "date", "time", "count"]

data = pd.read_csv(url, sep=",", header = None, names = ("type", "date", "time", "count"), parse_dates={'datetime': ['date', 'time']}, index_col='datetime')

OUTFLOW_ID = 7
ppl_inside = 0
y_arr = np.zeros((0, 2))
i = 0;
for index, row in data.iterrows():
    if row['type'] == OUTFLOW_ID:
        ppl_inside -= row['count']
    else:
        ppl_inside += row['count']
    if(i % 2 != 0):
        y_arr = np.vstack((y_arr, [index, ppl_inside]))
    i+=1;


ts = data['count']
ts.head(10)


ys = np.array([ts[i] for i in  xrange(0,len(ts))])
EMOV_n = pd.Series(ys).ewm(com=2).mean()

Xs = np.ones(len(ys))

EMOV_n = EMOV_n.reshape(-1,1)
ys = ys.reshape(-1,1)

# RIDGE Regression
reg = linear_model.Ridge (alpha = 0.1)
reg.fit (EMOV_n, ys)
print reg.coef_
print np.mean(reg.predict(EMOV_n) - ys)

# Finding the week of the day
weeknames = []
for i in xrange (0, len(y_arr)):
    weeknames.append(y_arr[i, 0].weekday_name)
    weeknames.append(y_arr[i, 0].weekday_name)

calendar_days = []
for i in xrange (0, len(y_arr)):
    calendar_days.append(y_arr[i, 0].days_in_month)
    calendar_days.append(y_arr[i, 0].days_in_month)

month_numbers = []
for i in xrange (0, len(y_arr)):
    month_numbers.append(y_arr[i, 0].month)
    month_numbers.append(y_arr[i, 0].month)


hours = []
for i in xrange (0, len(y_arr)):
    hours.append(y_arr[i, 0].hour)
    hours.append(y_arr[i, 0].hour)

mins = []
for i in xrange (0, len(y_arr)):
    mins.append(y_arr[i, 0].minute)
    mins.append(y_arr[i, 0].minute)


weeknames = np.array(weeknames).reshape(-1,1)
calendar_days = np.array(calendar_days).reshape(-1,1)
month_numbers = np.array(month_numbers).reshape(-1,1)
hours = np.array(hours).reshape(-1,1)
mins = np.array(mins).reshape(-1,1)
Xtrain = EMOV_n
Xtrain = np.hstack((Xtrain, calendar_days))
Xtrain = np.hstack((Xtrain, month_numbers))
Xtrain = np.hstack((Xtrain, hours))
Xtrain = np.hstack((Xtrain, mins))

# RIDGE Regression
reg = linear_model.Ridge (alpha = 0.1)
reg.fit (Xtrain, ys)
print reg.coef_
print np.mean(reg.predict(Xtrain) - ys)
