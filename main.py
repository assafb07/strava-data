from tkinter import *
import sqlite3
from datetime import date, datetime, timedelta
import http.client, urllib.parse
import json
from threading import Thread
import tkinter as tk
from PIL import Image, ImageTk
from itertools import count, cycle
import os
import time
from tkinter import filedialog as fd
import calendar


bg = '#003057' ; fg = '#ffe8f7' ; button_bg = '#3d49a8'
label_bg = '#262d61' ; text_box_bg = '#d0dff5' ; abg = '#806b71'
afg = '#3b2e70' ; fnt = 'gisha' ; fnt_size = '12'
hi = '1' #buttons height;
wid = '27' #buttons width
s = 1
text_box_hight = 9

class ImageLabel(tk.Label):

    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)

        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100

        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()

    def unload(self):
        self.config(image=None)
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)

def when_close():
    os.remove("answers.db")
    print ('removing temp db from local disk')
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    connection.close()
    print ('closing connection with shoes_miles.db')
    root.destroy()

def update_json():
    try:
        filename = fd.askopenfile()
        print(filename.name)
        with open('updated.json', 'r') as main_json:
            main_json = main_json.read()
            txt01 = main_json[:-1]+','
        with open (filename.name) as file02:
            file02 = file02.read()
            txt02 = file02[1:]

            new_file = txt01 + txt02
            with open ("updated.json", 'w') as updated:
                updated.write(new_file)
        print ('json update is done')

    except: print ('no file, no update')

    with open (filename.name) as file02: #read all activities json and analize
        raw_data = json.load(file02)
        activity = raw_data[0]
        distance_meter = activity["distance"]
        print (distance_meter)
        gear_id = (activity["gear_id"])
        print (gear_id)
        updated_miles = update_shoe(gear_id,distance_meter)


def update_shoe(gear_id,new_ks):
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    val  = (gear_id,)
    sql = "select ks from shoes_miles where gear_id = ?"
    with connection:
        cursor.execute(sql,val)
        old_ks = cursor.fetchone()
        new_ks = (new_ks/1000) + old_ks[0]
        val = (new_ks,gear_id)
        sql = "update shoes_miles set ks = ? where gear_id = ?"
        cursor.execute(sql, val)


def refresh():
    os.remove("answers.db")
    x=1
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    connection.execute("drop table all_activities")
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

    f = open("updated.json")
    raw_data = json.load(f)

    for activity in raw_data:
        if activity['sport_type'] != 'Run' and int(activity['distance']) < 100:
            continue
        else:
            x +=1
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
    print(x)


    f.close()
    connection.close()
    print ('removing temp db from local disk')

    th01 = Thread(target=add_location_th01)
    th01.start()
    th02 = Thread(target=add_location_th02)
    th02.start()
    th03 = Thread(target=long_fast_year)
    th03.start()
    th04 = Thread(target=summary)
    th04.start()
    time.sleep(0.1)
    th05 = Thread(target=all_shoes)
    th05.start()
    th01.join()
    th02.join()
    th03.join()
    th04.join()
    th05.join()
    text_box = Text(root, height=text_box_hight, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    text_box.insert(1.0, 'Updated!! ')
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)

def return_answers():
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()

    #3 best 5k
    sql = 'SELECT * FROM all_activities WHERE distance>5000 AND distance < 5100 ORDER BY pace limit 0,3'
    with connection:
        cursor.execute(sql)
        answer03 = cursor.fetchall()
        table_name03 = 'best_five'
        answers_dic = {table_name03 : answer03}

    #4 best 10k
    sql = 'SELECT * FROM all_activities WHERE distance>=10000 AND distance < 10100 ORDER BY pace limit 0,3'
    with connection:
        cursor.execute(sql)
        answer04 = cursor.fetchall()
        table_name04 = 'best_ten'
        answers_dic[table_name04] = answer04


    #7 best half marathon
    sql = 'SELECT * FROM all_activities WHERE distance>=21100 AND distance < 21200 ORDER BY pace limit 0,3'
    with connection:
        cursor.execute(sql)
        answer07 = cursor.fetchall()
        table_name07 = 'best_half'
        answers_dic[table_name07] = answer07

    #8best marathon
    sql = 'SELECT * FROM all_activities WHERE distance>=42192 AND distance < 43300 ORDER BY pace limit 0,1'
    with connection:
        cursor.execute(sql)
        answer08 = cursor.fetchall()
        table_name08 = 'best_marathon'
        answers_dic[table_name08] = answer08

    return answers_dic.items()


def return_answers01():
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    #1 max hr run
    sql = 'SELECT * from all_activities order by max_hr desc limit 0,3'
    with connection:
        cursor.execute(sql)
        answer01 = cursor.fetchall()
        table_name01 = 'maximum_hr'
        answers_dic = {table_name01 : answer01}

    #5all ultras
    sql = 'SELECT * FROM all_activities WHERE distance > 42000 order by distance desc'
    with connection:
        cursor.execute(sql)
        answer05 = cursor.fetchall()
        table_name05 = 'best_ultras'
        answers_dic[table_name05] = answer05

    #6 highest avarage hr
    sql = 'SELECT * from all_activities order by avg_hr DESC LIMIT 0,3'
    with connection:
        cursor.execute(sql)
        answer06 = cursor.fetchall()
        table_name06 = 'high_avg_hr'
        answers_dic[table_name06] = answer06


    #9best mile
    sql = 'SELECT * from all_activities WHERE distance >1600 and distance < 1700 ORDER BY pace LIMIT 0,3'
    with connection:
        cursor.execute(sql)
        answer09 = cursor.fetchall()
        table_name09 = 'best_mile'
        answers_dic[table_name09] = answer09
    return answers_dic.items()

def create_tables():
    answers = return_answers()
    connection = sqlite3.connect('answers.db')
    cursor = connection.cursor()

    for key,value in answers:
        sql = """CREATE TABLE %s(
                id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                date text,
                distance REAL,
                pace REAL,
                avg_hr REAL,
                max_hr REAL,
                gear text,
                neighbourhood text,
                city text,
                state text)
                """ % key

        connection.execute(sql)
    return answers

def create_tables01():
    answers = return_answers01()
    connection = sqlite3.connect('answers.db')
    cursor = connection.cursor()

    for key,value in answers:
        sql = """CREATE TABLE %s(
                id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                date text,
                distance REAL,
                pace REAL,
                avg_hr REAL,
                max_hr REAL,
                gear text,
                neighbourhood text,
                city text,
                state text)
                """ % key

        connection.execute(sql)
    return answers

def add_location_th01():
    run_loc01 = create_tables()
    for key,value in run_loc01:
        print ('thread 01', key)
        for answer in value:
            longitude = answer[6]
            latitude = answer[7]
            location = find_location(longitude, latitude)
            neighbourhood = location[0]
            city = location[1]
            state = location[2]
            connection = sqlite3.connect('answers.db')
            cursor = connection.cursor()
            val = (answer[0], answer[1], answer[2], answer[3], answer[4], answer[5], neighbourhood, city, state)
            sql = """INSERT INTO %s (date, distance, pace, avg_hr, max_hr, gear, neighbourhood, city, state) VALUES (?,?,?,?,?,?,?,?,?)""" % key
            with connection:
                cursor.execute(sql, val)


def add_location_th02():
    run_loc02 = create_tables01()
    for key,value in run_loc02:
        print ('thread 02', key)
        for answer in value:
            longitude = answer[6]
            latitude = answer[7]
            location = find_location(longitude, latitude)
            neighbourhood = location[0]
            city = location[1]
            state = location[2]
            connection = sqlite3.connect('answers.db')
            cursor = connection.cursor()
            val = (answer[0], answer[1], answer[2], answer[3], answer[4], answer[5], neighbourhood, city, state)
            sql = """INSERT INTO %s (date, distance, pace, avg_hr, max_hr, gear, neighbourhood, city, state) VALUES (?,?,?,?,?,?,?,?,?)""" % key
            with connection:
                cursor.execute(sql, val)

def find_location(longitude,latitude):
    #get longitude,latitude from strava json and request city and neighbourhood, country from api.positionstack.com
    try:
        conn = http.client.HTTPConnection('api.positionstack.com')
        x = str(latitude)+','+str(longitude)
        params = urllib.parse.urlencode({
            'access_key': '<api token here>',
            'query': x,
            'fields': 'results.neighbourhood',
            'limit': '1'
            })
        conn.request('GET', '/v1/reverse?{}'.format(params))
        res = conn.getresponse()
        data = res.read().decode()
        js = json.loads(data)
        a = ((js["data"])[0])
        location = (a["neighbourhood"], a["locality"], a["country"])
        conn.close()
    except:
        location = ('neighbourhood', 'city', 'state')
    return (location)

def read_table(table_name):
    th01.join()
    th02.join()
    connection = sqlite3.connect('answers.db')
    cursor = connection.cursor()
    val = (table_name,)
    sql = "SELECT * from %s" % val
    with connection:
        rn = cursor.execute(sql)

    return rn

def insert_runs(i):
    match i:
        case 1:# max hr run
            table_name = 'maximum_hr'
            runs = read_table(table_name)
        case 3:#3 best 5k
            table_name = 'best_five'
            runs = read_table(table_name)
        case 4:#4 best 10k
            table_name = 'best_ten'
            runs = read_table(table_name)
        case 5:#5all ultras
            table_name = 'best_ultras'
            runs = read_table(table_name)
        case 6:#6 highest avarage hr
            table_name = 'high_avg_hr'
            runs = read_table(table_name)
        case 7:#7 best half marathon
            table_name = 'best_half'
            runs = read_table(table_name)
        case 8:#8best marathon
            table_name = 'best_marathon'
            runs = read_table(table_name)
        case 9:#9best mile
            table_name = 'best_mile'
            runs = read_table(table_name)

    x = 1 ; y = 1
    text_box = Text(root, height=text_box_hight, width=50, bg = text_box_bg, font=(fnt,fnt_size))

    for run in runs:

        index01 = f'{x}.0'
        shoe = get_shoe_name(run[6])
        ks = (run[2])/1000
        pace = run[3]
        atime = ks * pace
        print_time = make_time(atime)
        print_pace = make_time(run[3])
        neighbourhood = run[7]
        city = run[8]
        state = run[9]
        to_print = (f'{y}:{run[1]}\n  Distance: {round(ks,3)}Km\n  Time: {print_time}\n  Pace: {print_pace}\n  Max HR: {run[5]}\n  Avarage HR: {run[4]}\n  Shoe: {shoe[0]} \n  Location: {neighbourhood}, {city}, {state}\n\n')

        text_box.insert(index01, to_print)
        x += 9 ; y += 1
    x += 9
    index01 = f'{x}.0'
    text_box.insert(index01, '\ninformation from Strava API \nLocations with positionstack API')
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)

def all_shoes():
    print ('thrad 05')
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()

    with connection:
        cursor.execute('SELECT * from shoes_miles order by  gear_id')
        all_shoes = cursor.fetchall()
    x = 0
    all_last = []
    with open('updated.json') as f: #find last run date for each shoe
        raw_data = json.load(f)

    connection = sqlite3.connect('answers.db')
    cursor = connection.cursor()
    sql = """CREATE table all_shoes (
            id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name text,
            distance REAL,
            last_run text)"""
    with connection:
        cursor.execute(sql)

    for shoe in all_shoes:
    #    print (f'{x}: {shoe[1]} - {shoe[2]}ks')
        gear_id = shoe[0]
        for activity in raw_data:
            if gear_id == activity["gear_id"]:
                activity_date = (activity["start_date_local"])
                date = activity_date[0:10]
            else:
                continue

        sql = """INSERT into all_shoes (name,distance,last_run) VALUES (?,?,?)"""
        val = (shoe[1], shoe[2], date)
        with connection:
            cursor.execute(sql,val)

def print_shoes():
    text_box = Text(root, height=text_box_hight, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    x = 1
    connection = sqlite3.connect('answers.db')
    cursor = connection.cursor()
    with connection:
        cursor.execute("select * from all_shoes order by last_run DESC")
        shoes_db = cursor.fetchall()

        for shoe in shoes_db:
            to_print = (f'{shoe[1]}\nshoe milege: {shoe[2]}ks\nlast run: {shoe[3]}\n\n')
            text_box.insert(f'{x}.0', to_print)
            x += 4
    text_box.insert(f'{x}.0', '\ninformation from Strava API \nLocations with positionstack API')
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)


def last_run():
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    with connection:
        cursor.execute('select * from all_activities order by date DESC')
        last_run_l = cursor.fetchone()
    return last_run_l

def print_last_run():

    last_run_l = last_run()

    today = date.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    sql = "SELECT ks from shoes_miles where gear_id=?"
    val= (last_run_l[5],)
    with connection:
        cursor.execute(sql,val)
        shoe_ks = cursor.fetchall()
        cursor.execute("select * from all_activities")
        all = cursor.fetchall()
    week_ks = 0
    for item in all:
        if item[0] >= str(start) and item[0]< str(end):
            week_ks = week_ks + float(item[1])

        else: continue
    print (round(week_ks/1000,2))
    shoe = get_shoe_name(last_run_l[5])
    ks = (last_run_l[1])/1000
    pace = last_run_l[2]
    atime = ks * pace
    print_time = make_time(atime)
    print_pace = make_time(last_run_l[2])

    longitude  = last_run_l[6]
    latitude = last_run_l[7]
    location = find_location(longitude,latitude)
    neighbourhood = location[0]
    city = location[1]
    state = location[2]
    text_box = Text(root, height=text_box_hight, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    text_box.insert (1.0, f'Last Run: {last_run_l[0]}\nDistance: {round(ks,3)}Km\nTime: {print_time}\nPace: {print_pace}\nMax HR: {last_run_l[4]}\nAvarage HR: {last_run_l[3]}\nShoe: {shoe[0]} ({round(shoe_ks[0][0],1)}Km) \nLocation:{neighbourhood}, {city}, {state}\nDistance this week: {round(week_ks/1000,2)} Km\n\n')
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)

def summary():
    #fetch first activity recoreded date
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    with connection:
        cursor.execute('select * from all_activities order by date')
        first_date = cursor.fetchone()


    with open('updated.json') as f: #read all activities json and analize
        raw_data = json.load(f)
    over_all_distance = 0
    over_all_time = 0
    over_all_elv = 0
    hr_sum = 0
    x = 0 #total number of runs
    no_hr = 0 # no hr record counter
    no_cad = 0 #no cadance record counter
    pace_distance_sum = 0
    cadance_sum = 0
    #over all distance, elevation, calculate avarage pace (sum(pace*distance) / total distance), avg heart rate (sum run_avg_hr / num of runs)
    for item in raw_data:
        if item['sport_type'] != 'Run' and int(item['distance']) < 100:
            continue
        else:
            x +=1

            distance = float(item["distance"])/1000
            over_all_distance = over_all_distance + distance
            atime = float(item["moving_time"])/60
            over_all_time = over_all_time + atime
            elv = item["total_elevation_gain"]
            over_all_elv = over_all_elv + elv
            try:
                hr_sum = hr_sum + item["average_heartrate"]
            except:
                no_hr +=1
            pace_distance = float(item["average_speed"]) * distance
            pace_distance_sum = pace_distance_sum + pace_distance
            try:
                cadance_sum = cadance_sum + int(item["average_cadence"])
            except:
                no_cad +=1

    atime = make_time(over_all_time)
    with_steps = x - no_cad
    with_monitor = x-no_hr
    total_avg_hr = hr_sum / (x-no_hr)
    total_avg_pace = 60/((pace_distance_sum / over_all_distance)*3.6)
    pace = make_time(total_avg_pace)
    total_avg_cadance = 2*(cadance_sum / (x-no_cad))
    connection = sqlite3.connect('answers.db')
    cursor = connection.cursor()
    sql = """create table summery
            (total_dis REAL,
            total_time text,
            total_elv REAL,
            all_runs REAL,
            total_avg_hr REAL,
            with_monitor REAL,
            total_avg_pace text,
            avg_cad REAL,
            with_steps REAL,
            first_run text,
            first_distance REAL
             )"""
    with connection:
        cursor.execute(sql)

    connection01 = sqlite3.connect('answers.db')
    cursor01 = connection01.cursor()
    sql = """INSERT INTO summery (total_dis, total_time, total_elv, all_runs, total_avg_hr, with_monitor, total_avg_pace, avg_cad, with_steps, first_run, first_distance) VALUES (?,?,?,?,?,?,?,?,?,?,?)"""
    val = (over_all_distance, atime, over_all_elv, x, total_avg_hr, with_monitor , pace, total_avg_cadance, with_steps, first_date[0], first_date[1]/1000)
    print ('thread 04')
    with connection01:
        cursor01.execute(sql,val)

def print_summery():
    connection = sqlite3.connect('answers.db')
    cursor = connection.cursor()
    with connection:
        cursor.execute("SELECT * from summery")
        from_db = cursor.fetchall()
        summery_answers = from_db[0]

    text_box = Text(root, height=text_box_hight, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    text_box.insert(1.0, f'Over all distance: {round(summery_answers[0],2)} Km\n\n')#    print ('distance',round (over_all_distance,2))
    text_box.insert(3.0, f'Over all time running: {summery_answers[1]}\n\n')#    print ('time',round(over_all_time,2))
    text_box.insert(5.0, f'Total elevation gain: {round(summery_answers[2],2)} meter\n\n')#    print ('total_elevation_gain',round(over_all_time,2))
    text_box.insert(7.0, f'Total number of runs {summery_answers[3]}\n\n')#    print ('total number of runs', x)
    text_box.insert(9.0, f'Total avarage heart hate: {int(summery_answers[4])} bpm\n\n')#    print ('total_avg_hr', total_avg_hr)
    text_box.insert(11.0, f'Runs with Heart Rate Monitor: {summery_answers[5]}\n\n')#    print ('run with hr monitor', x-no_hr)

    text_box.insert(13.0, f'Total avarage pace: {summery_answers[6]}\n\n')#    print ('avarage pace',total_avg_pace )
    text_box.insert(15.0, f'Avarage Cadance: {round(summery_answers[7],2)}\n\n')#    print ('avarage cadance',total_avg_cadance )
    text_box.insert(17.0, f'Runs with steps counter: {summery_answers[8]}\n\n')#    print ('runs with steps counter', x-no_cad)
    text_box.insert(19.0, f'First run recorded on Strava: {summery_answers[10]}Km on {summery_answers[9]}\n\n')
    text_box.insert(21.0, 'information from strava.api')

    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)

def get_shoe_name(gear_id):
    #shoes_miles table create by add_and_update_shoes_db.py and jsons from strava api
    #get the shoe for specific run
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    sql = 'select name from shoes_miles where gear_id = ?'
    val  = (gear_id,)
    with connection:
        try:
            cursor.execute(sql,val)
            shoe_name = cursor.fetchall()[0]
        except:
            shoe_name = 'None'
    connection.close()
    return shoe_name

def make_time(atime):
    if atime > 60:
        hour = int(atime/60)
        min_re = atime-(hour*60)
        min = int(min_re)
        sec = int((min_re-min)*60)
        hour_min_sec = f"{hour} hours {min} min {sec} sec"
        return hour_min_sec
    else:
        min = int(atime)
        sec = int((atime-min)*60)
        min_sec = f"{min} min {sec} sec"
        return min_sec


def this_year():
    #make a list of all the runs in chosen year (this year)
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    #1 max hr run
    sql = 'SELECT * from all_activities'
    with connection:
        cursor.execute(sql)
        all = cursor.fetchall()
    year_runs = []
    best_run = []
    pace_cach = 100
    distance_cach = 0
    best = 0
    today = datetime.today().strftime("%Y")
    for item in all:
        date = item[0]
        year = int(date[0:4])
        if year == int(today):
            year_runs.append(item)
        else:
            continue

    return year_runs


def mile_prediction():
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    sql = 'SELECT * from all_activities'
    with connection:
        cursor.execute(sql)
        all = cursor.fetchall()
    mile_for_now = 0
    distance_cach = 0

    today = datetime.today().strftime("%Y")
    number_of_days = datetime.now().timetuple().tm_yday

    for item in all:
        date = item[0]
        year = int(date[0:4])
        if year == int(today):
            mile_for_now = (mile_for_now + item[1])
        else:
            continue

    year_prediction = mile_for_now / number_of_days * 365 / 1000


    text_box = Text(root, height=text_box_hight, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    to_print = (f'{round(mile_for_now/1000,2)}Km this year\nAll year miles prediction: {int(year_prediction)}Km\n\n\n')

    text_box.insert(1.0, to_print)
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)

def long_fast_year():
    year_runs = this_year()
    distance = lambda year_runs : year_runs[1]
    year_runs.sort(key=distance, reverse = True)
    answers_dic01 = {'long_year' : year_runs[0]}

    pace = lambda year_runs : year_runs[2]
    year_runs.sort(key=pace, reverse = False)
    answers_dic01['fast_run'] = year_runs[0]

    for key,value in answers_dic01.items():
        print (key, 'thread 03')
        longitude  = value[6]
        latitude = value[7]
        location = find_location(longitude,latitude)
        neighbourhood = location[0]
        city = location[1]
        state = location[2]
        pace = value[2]
        distance = value[1]
        max_hr = value[4]
        avg_hr = value[3]
        gear = value[5]


        connection = sqlite3.connect('answers.db')
        cursor = connection.cursor()
        sql01 = """drop table IF EXISTS %s""" % key
        connection.execute(sql01)
        sql = """CREATE TABLE %s(
            id  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            date text,
            distance REAL,
            pace REAL,
            avg_hr REAL,
            max_hr REAL,
            gear text,
            neighbourhood text,
            city text,
            state text)
            """ % key

        connection.execute(sql)
        val = (value[0], value[1], value[2], value[3], value[4], value[5], neighbourhood, city, state)
        sql = """INSERT INTO %s (date, distance, pace, avg_hr, max_hr, gear, neighbourhood, city, state) VALUES (?,?,?,?,?,?,?,?,?)""" % key
        with connection:
            cursor.execute(sql, val)

def print_best_year(i):
    connection = sqlite3.connect('answers.db')
    cursor = connection.cursor()
    match i:
        case 11:# long run yeas year
            with connection:
                cursor.execute("select * from long_year")
                best_year = cursor.fetchall()[0]

        case 12:# fasr run yeas year
            with connection:
                cursor.execute("select * from fast_run")
                best_year = cursor.fetchall()[0]


    shoe = get_shoe_name(best_year[6])
    ks = (best_year[2])/1000
    atime = ks * best_year[3]
    print_time = make_time(atime)
    print_pace = make_time(best_year[3])
    text_box = Text(root, height=text_box_hight, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    to_print = (f'{best_year[1]}\n  Distance: {round(ks,3)}Km\n  Time: {print_time}\n  Pace: {print_pace}\n  Max HR: {best_year[5]}\n  Avarage HR: {best_year[4]}\n  Shoe: {shoe[0]} \n  Location: {best_year[7]}, {best_year[8]}, {best_year[9]}\n\n')

    text_box.insert(1.0, to_print)
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)


def this_month():
    month_runs = []
    total_distance = 0
    x=0
    total_pace = 0
    total_hr = 0
    longest_run = 0
    this_year_runs = this_year()
    today = datetime.today().strftime("%m")

    for item in this_year_runs:
        date = item[0]
        ymd = date.split('-')
        this_month = int(ymd[1])
        if this_month == int(today):
            x+=1
            print(item)
            if item[1] > longest_run:
                longest_run = item[1]
            total_distance = (item[1])+ total_distance
            print(total_distance)
            total_pace = (item[2]) + total_pace
            total_hr = item[3] + total_hr
        else:
            continue


    distance = (round(total_distance/1000,2))
    avg_pace = total_pace / x
    pace = make_time(avg_pace)
    avg_hr = total_hr / x
    print (x,distance)
    text_box = Text(root, height=text_box_hight, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    to_print = (f'Total Distance this month({calendar.month_name[int(today)]}): {distance}\nAvarage Pace: {pace}\nAvarage Heart Rate: {round(avg_hr,2)}\nLongest Run: {round(longest_run/1000,2)}Ks\n')
    text_box.insert(1.0, to_print)
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)

def load_frame():
    splash.destroy()

    label01 = Label(root, text='         Strava Numbers      ', font=(fnt,'34'),fg=fg, bg=bg)
    label01.grid(row=0, columnspan=2)

    bt09 = Button(root,text="Fastest Run this year", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:print_best_year(12))
    bt09.grid(row=3,column=0)

    bt10 = Button(root,text="Longest Run this year", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:print_best_year(11))
    bt10.grid(row=3,column=1)

    bt11 = Button(root,text="All Shoes", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:print_shoes())
    bt11.grid(row=4,column=0)

    bt12 = Button(root,text="Summary", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:print_summery())
    bt12.grid(row=2,column=1)

    bt13 = Button(root,text="Last Run", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:print_last_run())
    bt13.grid(row=1,column=0)

    bt14 = Button(root,text="This Month Summery", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:this_month())
    bt14.grid(row=1,column=1)

    bt15 = Button(root,text="Year Miles prediction", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:mile_prediction())
    bt15.grid(row=2,column=0)

    bt01 = Button(root,text="5k best", font=(fnt,fnt_size),  fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(3))
    bt01.grid(row=4,column=1)

    bt02= Button(root,text="Best 10k", font=(fnt,fnt_size),  fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(4))
    bt02.grid(row=5,column=0)

    bt03 = Button(root,text="Best Half Marathon", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(7))
    bt03.grid(row=5,column=1)

    bt04 = Button(root,text="Best Marathon", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(8))
    bt04.grid(row=6,column=0)

    bt05 = Button(root,text="Best Mile", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(9))
    bt05.grid(row=6,column=1)

    bt06 = Button(root,text="Best Runs this year", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(10))
    bt06.grid(row=7,column=0)

    bt06 = Button(root,text="All Marathon and Ultras", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(5))
    bt06.grid(row=7,column=1)

    bt07 = Button(root,text="Highest MAX HR recorded", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(1))
    bt07.grid(row=8,column=0)

    bt08 = Button(root,text="Highest Avarage HR", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(6))
    bt08.grid(row=8,column=1)

    text_box = Text(root, height=text_box_hight, width=50,bg = text_box_bg, font=(fnt,fnt_size))
    text_box.insert(1.0, f'Analizing your strava activities\nData gethered with Strava API v3, Swagger UI\nLocations with positionstack API (positionstack.com)\ncoded by abmail07@gmail.com')
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=345)



try:
    os.remove("answers.db")
except:
    print ('no temp files')


splash = tk.Tk()
splash.title("Strava Numbers")
splash.geometry('540x630+350+50')
splash.configure(bg = 'white')
label01 = tk.Label(splash, text='   Strava Numbers ', font=(fnt,'35'),bg='white')
label01.pack()

lbl = ImageLabel(splash)
lbl.pack()
lbl.load('run02.gif')
splash.overrideredirect(True)
label02 = tk.Label(splash, text='\nAnalizing your strava activities', font=(fnt,'25'),bg='white')
label02.pack()
label03 = tk.Label(splash, text='Data gethered with Strava API v3, Swagger UI', font=(fnt,'16'),bg='white')
label03.pack()
label04 = tk.Label(splash, text='Locations with positionstack API (positionstack.com)', font=(fnt,'16'),bg='white')
label04.pack()

th01 = Thread(target=add_location_th01)
th01.start()
th02 = Thread(target=add_location_th02)
th02.start()
th03 = Thread(target=long_fast_year)
th03.start()
th04 = Thread(target=summary)
th04.start()
time.sleep(0.1)
th05 = Thread(target=all_shoes)
th05.start()



root = Tk()
root.title("Strava Numbers")
root.geometry('507x550+350+50')
root.protocol("WM_DELETE_WINDOW", when_close)
root.after(3000, load_frame)
root.option_add('*tearOff', False)
menubar = Menu(root)
root.config(menu = menubar)
file = Menu(menubar)
update = Menu(menubar)
menubar.add_cascade(menu = file, label = 'Update')
file.add_command(label = 'New Activities', command = lambda: update_json())
menubar.add_cascade(menu = update, label = 'Refresh')
update.add_command(label = 'Refresh', command = lambda: refresh())

splash.mainloop()
