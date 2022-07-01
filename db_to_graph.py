import sqlite3
import datetime
import matplotlib.pyplot as plt

date_list =[]
pace_list = []
distance_list = []
avg_hr_list = []
count_pace = 0
count_date = 0


def make_graph(x,y):
    plt.scatter(x, y, label= "stars", color= "green",
                marker= "*", s=30)
# x-axis label
    plt.xlabel('x - Date')
# frequency label
    plt.ylabel('y '+title)
# plot title
    plt.title('Strava History')
# showing legend
    plt.legend()
# function to show the plot
    plt.show()

connection = sqlite3.connect('shoes_miles.db')
cursor = connection.cursor()
with connection:
    sql = 'SELECT pace FROM all_activities order by date '
    cursor.execute(sql)
    all_pace = cursor.fetchall()
    sql = 'SELECT date FROM all_activities order by date'
    cursor.execute(sql)
    all_date = cursor.fetchall()
    sql = 'SELECT avg_hr FROM all_activities order by date '
    cursor.execute(sql)
    all_avg_hr = cursor.fetchall()
    sql = 'SELECT distance FROM all_activities order by date '
    cursor.execute(sql)
    all_distance = cursor.fetchall()
connection.close()


for item in all_date:
    date = (item[0])
    year = int(date[0:4])
    date_list.append(date)
for item in all_pace:
    pace = item[0]
    pace_list.append(pace)
for item in all_distance:
    distance = item[0]/1000
    distance_list.append(distance)
for item in all_avg_hr:
    hr = item[0]
    avg_hr_list.append(hr)

i = int(input('choose graph: 1 for pace, 2 for distance, 3 for hr...'))
if i == 1:
    title = 'pace'
    make_graph(date_list,pace_list)
elif i == 2:
    title = 'distance'
    make_graph(date_list,distance_list)
else:
    title = 'avarage hr'
    make_graph(date_list,avg_hr_list)






print (date_list)
print (pace_list)
