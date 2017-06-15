import pandas as pd
import numpy as np
import matplotlib.pylab as plt
from sklearn import linear_model

url="https://archive.ics.uci.edu/ml/machine-learning-databases/event-detection/CalIt2.data"
data = pd.read_csv(url, sep=",", header = None)
data.columns = ["type", "date", "time", "count"]
print data.head()
print '\n Data Types:'
print data.dtypes
print data.index

data = pd.read_csv(url, sep=",", header = None, names = ("type", "date", "time", "count"), parse_dates={'datetime': ['date', 'time']}, index_col='datetime')
print data.head()
print 'Data Types:'
print data.dtypes
print data.index


# Calculating the number of people in the building at different point of time in a day.
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
    
plt.plot(y_arr[:,0], y_arr[:,1])
plt.show()

ts = data['count']
ts.head(10)

plt.plot(ts)
plt.show()

ys = np.array([ts[i] for i in  xrange(0,len(ts))])
EMOV_n = pd.Series(ys).ewm(com=2).mean()
print EMOV_n

Xs = np.ones(len(ys))
print np.shape(Xs)

print np.shape(np.hstack((Xs, EMOV_n)))
# print np.shape(np.vstack())
print len(EMOV_n)

EMOV_n = EMOV_n.reshape(-1,1)
ys = ys.reshape(-1,1)

# LINEAR Regression
clf = linear_model.LinearRegression()
clf.fit(EMOV_n, ys)
print clf.coef_
print np.mean(clf.predict(EMOV_n) - ys)

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
    
weeknames = np.array(weeknames).reshape(-1,1)
calendar_days = np.array(calendar_days).reshape(-1,1)
month_numbers = np.array(month_numbers).reshape(-1,1)
Xtrain = EMOV_n
#Xtrain = np.hstack((Xtrain, weeknames))
Xtrain = np.hstack((Xtrain, calendar_days))
Xtrain = np.hstack((Xtrain, month_numbers))

# LINEAR Regression
clf = linear_model.LinearRegression()
clf.fit(Xtrain, ys)
print clf.coef_
print np.mean(clf.predict(Xtrain) - ys)

# RIDGE Regression
reg = linear_model.Ridge (alpha = 0.1)
reg.fit (Xtrain, ys)
print reg.coef_
print np.mean(reg.predict(Xtrain) - ys)

#Calculating holiday or not
from pandas.tseries.holiday import USFederalHolidayCalendar

df = pd.DataFrame()
#df['Date'] = y_arr[:,0]
df['Date'] = pd.date_range(start='2005-07-24', end='2005-11-05')

# df['Date'] = pd.date_range(start='2005-07-24', end='2005-11-05')
holiday_cal = USFederalHolidayCalendar()
holidays = holiday_cal.holidays(start='2005-07-24', end='2005-11-05')

df['Holiday'] = df['Date'].isin(holidays)
print df

# h_df = []
# for i in xrange(0, len(y_arr)):
#     print type(y_arr[i,0])
#     h_df.append(y_arr[i,0].isin(holidays))
# df['Holiday'] = h_df
# print df

Xtest = pd.date_range(start='2005-11-06', end='2005-11-10')

