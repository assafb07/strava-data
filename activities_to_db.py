import json
import sqlite3
import datetime



connection = sqlite3.connect('shoes_miles.db')
cursor = connection.cursor()
try:
    connection.execute("""CREATE TABLE all_activities (
            date text,
            distance REAL,
            pace REAL,
            avg_hr REAL,
            gear text

            )""")
except: print ('table exist. Move on')
activity_heart = 0
counter = 0
activity_speed_m = 0 # avarage speed in mile/h
distance_meter = 0
max_heartrate_cach = 0

# Opening JSON file
f = open('all_activities.json')

# returns JSON object as
# a dictionary
raw_data = json.load(f)


#first = raw_data[0]
for activity in raw_data:

    try:
        activity_heart = (activity["average_heartrate"])
        max_heartrate = (activity["max_heartrate"])

    except: activity_heart = 0
    activity_speed_m = (activity["average_speed"])
    distance_meter = (activity["distance"])
    gear_id = (activity["gear_id"])

    activity_date = (activity["start_date_local"])
    date = activity_date[0:10]
#date = datetime.datetime(max_h_date)

    pace =  60/(activity_speed_m*3.6)

    sql = 'INSERT INTO all_activities (date, distance, pace, avg_hr, gear) VALUES(?, ?, ?, ?, ?)'
    val = (date, distance_meter, pace, activity_heart, gear_id)
    with connection:
        sql = 'SELECT pace FROM all_activities '
        cursor.execute(sql)
        all_pace = cursor.fetchall()
        sql = 'SELECT date FROM all_activities '
        cursor.execute(sql)
        all_date = cursor.fetchall()
        sql = 'SELECT avg_hr FROM all_activities '
        cursor.execute(sql)
        all_avg_hr = cursor.fetchall()
        sql = 'SELECT distance FROM all_activities '
        cursor.execute(sql)
        all_distance = cursor.fetchall()
print (all_pace)







f.close()
connection.close()
