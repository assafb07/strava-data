from tkinter import *
import sqlite3
from datetime import datetime
import http.client, urllib.parse
import json
import io

def return_answer(i):
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    if i == 1: # max hr run
        sql = 'SELECT * from all_activities order by max_hr desc limit 0,3'
    elif i == 5: # all marathons and ultras
        sql = 'SELECT * FROM all_activities WHERE distance > 42000 order by distance desc'
    elif i == 6: # highest avarage hr
        sql = 'SELECT * from all_activities order by avg_hr DESC LIMIT 0,3'
    elif i == 3: # best 5k
        sql = 'SELECT * FROM all_activities WHERE distance>5000 AND distance < 5100 ORDER BY pace limit 0,3'
    elif i == 4 : # best 10k
        sql = 'SELECT * FROM all_activities WHERE distance>=10000 AND distance < 10100 ORDER BY pace limit 0,3'
    elif i == 7 : # best half marathon
        sql = 'SELECT * FROM all_activities WHERE distance>=21100 AND distance < 21200 ORDER BY pace limit 0,3'
    elif i == 8: #best marathon
        sql = 'SELECT * FROM all_activities WHERE distance>=42192 AND distance < 43300 ORDER BY pace limit 0,1'
    elif i == 9 : #best mile
        sql = 'SELECT * from all_activities WHERE distance >1600 and distance < 1700 ORDER BY pace LIMIT 0,3'
    elif i == 11 or 12 : #fastest and longest run this year
        sql = 'SELECT * from all_activities'

    with connection:
        cursor.execute(sql)
        answer = cursor.fetchall()
    connection.close()
    return answer

def insert_runs(i):
    all_activities = return_answer(i)
    if i == 11:
        all = this_year(all_activities)
        if all != []:
            runs = pace_year(all)
        else:
            runs = [('2011-11-11', 0.0, 0.0, 0.0, 0.0, '0',0,0)]#no data for this year
    elif i == 12:
        all = this_year(all_activities)
        if all != []:
            runs = fast_year(all)
        else:
            runs = [('2011-11-11', 0.0, 0.0, 0.0, 0.0, '0')]#no data for this year
    else:
        all = '1'
        runs = all_activities
    x = 1
    y = 1
    text_box = Text(root, height=11, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    for run in runs:
        index01 = f'{x}.0'
        shoe = get_shoe_name(run[5])
        ks = (run[1])/1000
        pace = run[2]
        atime = ks * pace
        print_time = make_time(atime)
        print_pace = make_time(run[2])
        longitude = run[6]
        latitude = run[7]
        location = find_location(longitude,latitude)
        if all == []:
            to_print = ('No run this year yet')
        else:
            to_print = (f'{y}:{run[0]}\n  Distance: {round(ks,3)}Km\n  Time: {print_time}\n  Pace: {print_pace}\n  Max HR: {run[4]}\n  Avarage HR: {run[3]}\n  Shoe: {shoe[0]} \n  Location: {location[0]}, {location[1]}, {location[2]}\n\n')

        text_box.insert(index01, to_print)
        x += 9
        y += 1
    x += 9
    index01 = f'{x}.0'
    text_box.insert(index01, '\ninformation from Strava API \nLocations with positionstack API')
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=320)

def fast_year(all):
    best_run = []
    distance_cach = 0
    for distance in all:
        if int(distance[1]) > distance_cach:
            distance_cach = int(distance[1])
            best = distance
        else: continue
    best_run.append(best)
    return best_run

def all_shoes():
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    with connection:
        cursor.execute('SELECT * from shoes_miles order by gear_id desc')
        all_shoes = cursor.fetchall()
    z = 0
    x = 1
    y = 1
    all_last = []
    f = open('15_16_17_18_19.json')
    raw_data = json.load(f)
    text_box = Text(root, height=11, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    for shoe in all_shoes:
        index01 = f'{x}.0'
        z += 1
        gear_id = shoe[0]
        for activity in raw_data:
            if gear_id == activity["gear_id"]:
                activity_date = (activity["start_date_local"])
                date = activity_date[0:10]
            else:
                continue
        to_print = (f'{z}:{shoe[1]}\n  shoe milege: {shoe[2]}ks\n  last run: {date}\n\n')
        text_box.insert(index01, to_print)
        x += 9
        y += 1
    x += 9
    index01 = f'{x}.0'
    text_box.insert(index01, '\ninformation from Strava API \nLocations with positionstack API')
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=320)


def summary():
    #fetch first activity recoreded date
    connection = sqlite3.connect('shoes_miles.db')
    cursor = connection.cursor()
    with connection:
        cursor.execute('select * from all_activities order by date')
        first_date = cursor.fetchone()
    connection.close()
    f = open('15_16_17_18_19.json')
    raw_data = json.load(f)
    over_all_distance = 0
    over_all_time = 0
    over_all_elv = 0
    hr_sum = 0
    x = 0
    no_hr = 0 # no hr record counter
    no_cad = 0 #no cadance record counter
    pace_distance_sum = 0
    cadance_sum = 0
    #over all distance
    for item in raw_data:
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
    total_avg_hr = hr_sum / (x-no_hr)
    total_avg_pace = 60/((pace_distance_sum / over_all_distance)*3.6)
    total_avg_cadance = 2*(cadance_sum / (x-no_cad))

    text_box = Text(root, height=11, width=50, bg = text_box_bg, font=(fnt,fnt_size))
    text_box.insert(1.0, f'Over all distance: {round(over_all_distance,2)} Km\n\n')
#    print ('distance',round (over_all_distance,2))
    atime = make_time(over_all_time)
    text_box.insert(3.0, f'Over all time running: {atime}\n\n')
#    print ('time',round(over_all_time,2))
    text_box.insert(5.0, f'Total elevation gain: {round(over_all_time,2)} meter\n\n')
#    print ('total_elevation_gain',round(over_all_time,2))
    text_box.insert(7.0, f'Total number of runs {x}\n\n')
#    print ('total number of runs', x)
    text_box.insert(9.0, f'Total avarage heart hate: {int(total_avg_hr)} bpm\n\n')
#    print ('total_avg_hr', total_avg_hr)
    text_box.insert(11.0, f'Runs with Heart Rate Monitor: {x-no_hr}\n\n')
#    print ('run with hr monitor', x-no_hr)
    pace = make_time(total_avg_pace)
    text_box.insert(13.0, f'Total avarage pace: {pace}\n\n')
#    print ('avarage pace',total_avg_pace )
    text_box.insert(15.0, f'Avarage Cadance: {int(total_avg_cadance)}\n\n')
#    print ('avarage cadance',total_avg_cadance )
    text_box.insert(17.0, f'Runs with steps counter: {x-no_cad}\n\n')
#    print ('runs with steps counter', x-no_cad)
    text_box.insert(19.0, f'First run recorded on Strava: {first_date[0]}, {first_date[1]/1000}Km\n\n')
    text_box.insert(21.0, 'information from strava.api')

    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=320)

def get_shoe_name(gear_id):
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

def this_year(all):
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

def pace_year(all):
    pace_cach = 100
    best_run = []
    for pace in all:
        if int(pace[2]) > 0 and int(pace[2]) < pace_cach:
            pace_cach = pace[2]
            best = pace
        else:
            continue
    best_run.append(best)
    return best_run

def find_location(longitude,latitude):
    conn = http.client.HTTPConnection('api.positionstack.com')
    x = str(latitude)+','+str(longitude)
    params = urllib.parse.urlencode({
        'access_key': '96b9b8bcb8019702345235d94ff3cd99',
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
    return location

def load_frame():
    label01 = Label(root, text='         Strava Numbers       ', font=(fnt,'35'),fg=fg, bg=bg)
    label01.grid(row=0, columnspan=2)

    bt01 = Button(root,text="5k best", font=(fnt,fnt_size),  fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(3))
    bt01.grid(row=1,column=0)

    bt02= Button(root,text="Best 10k", font=(fnt,fnt_size),  fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(4))
    bt02.grid(row=1,column=1)

    bt03 = Button(root,text="Best Half Marathon", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(7))
    bt03.grid(row=2,column=0)

    bt04 = Button(root,text="Best Marathon", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(8))
    bt04.grid(row=2,column=1)

    bt05 = Button(root,text="Best Mile", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(9))
    bt05.grid(row=3,column=0)

    bt06 = Button(root,text="Best Runs this year", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(10))
    bt06.grid(row=3,column=1)

    bt06 = Button(root,text="All Marathon and Ultras", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(5))
    bt06.grid(row=3,column=1)

    bt07 = Button(root,text="Highest Hr MAX ever", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(1))
    bt07.grid(row=4,column=0)

    bt08 = Button(root,text="Highest Avarage HR", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(6))
    bt08.grid(row=4,column=1)

    bt09 = Button(root,text="Fastest Run this year", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(11))
    bt09.grid(row=5,column=0)

    bt10 = Button(root,text="Longest Run this year", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:insert_runs(12))
    bt10.grid(row=5,column=1)

    bt11 = Button(root,text="All Shoes I Ever Run", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:all_shoes())
    bt11.grid(row=6,column=0)

    bt12 = Button(root,text="Summary", font=(fnt,fnt_size), fg=fg, bg=button_bg, activebackground = abg,
    activeforeground = afg, height = hi, width = wid, command=lambda:summary())
    bt12.grid(row=6,column=1)

    text_box = Text(root, height=11, width=50,bg = text_box_bg, font=(fnt,fnt_size))
    text_box.tag_add("left", 1.0, "end")
    text_box.place(x=16, y=320)

bg = '#003057'
fg = '#ffe8f7'
button_bg = '#3d49a8'
label_bg = '#262d61'
text_box_bg = '#d0dff5'
abg = '#806b71'
afg = '#3b2e70'
fnt = 'gisha'
fnt_size = '14'
hi = '1'
wid = '24'

root = Tk()
root.geometry('548x590')
root.configure(bg=bg)
frame = Frame(root)

load_frame()
root.mainloop()
