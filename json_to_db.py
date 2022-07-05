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
            max_hr REAL,
            gear text,
            longitude REAL,
            latitude REAL

            )""")
except: print ('table exist. Move on')
activity_heart = 0
counter = 0
activity_speed_m = 0 # avarage speed in mile/h
distance_meter = 0
max_heartrate_cach = 0

f = open('15_16_17_18_19.json')
raw_data = json.load(f)

for activity in raw_data:

    try:
        activity_heart = (activity["average_heartrate"])
        max_heartrate = (activity["max_heartrate"])

    except:
        activity_heart = 0
        max_heartrate = 0
    try:
        latitude = (activity["start_latlng"][0])
        longitude = (activity["start_latlng"][1])
    except:
        latitude =  0
        longitude = 0

    activity_speed_m = (activity["average_speed"])
    distance_meter = (activity["distance"])
    gear_id = (activity["gear_id"])
    activity_date = (activity["start_date_local"])
    date = activity_date[0:10]
    try:
        pace =  60/(activity_speed_m*3.6)
    except:
        pace = 0
    sql = 'INSERT INTO all_activities (date, distance, pace, avg_hr, max_hr, gear, latitude, longitude) VALUES(?,?,?,?,?,?,?,?)'
    val = (date, distance_meter, pace, activity_heart, max_heartrate, gear_id, latitude, longitude)
    with connection:
        cursor.execute(sql,val)



f.close()
connection.close()
