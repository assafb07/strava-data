import json
import sqlite3

db_list = []

connection = sqlite3.connect('shoes_miles.db')
cursor = connection.cursor()

def new_gear_to_swager(gear_id):
    try:
        connection.execute("""CREATE TABLE gear_swagger (
                gear_id text
                )""")
    except:
        print ('table exist. Move on')
    sql = 'INSERT INTO  gear_swagger (gear_id) VALUES(?)'
    val = (gear_id,)
    with connection:
        cursor.execute(sql,val)


try:
    connection.execute("""CREATE TABLE shoes_miles (
            gear_id text,
            name text,
            ks REAL

            )""")
except: print ('table exist. Move on')

connection = sqlite3.connect('shoes_miles.db')
cursor = connection.cursor()

cursor.execute('SELECT gear_id FROM shoes_miles')
all_gear = cursor.fetchall()

for item in all_gear:
    db_list.append(item[0])


shoe_id_list = []
f = open('all_activities.json')

raw_data = json.load(f)

for line in raw_data:
    shoe_id = (line["gear_id"])
    if shoe_id in shoe_id_list:
        continue
    else:
        shoe_id_list.append(shoe_id)
print (shoe_id_list)

#read from gear files thst i created with swgger and rxtract name and mile for shoes
for gear_id in shoe_id_list:
    if gear_id == None: continue
    else:
#read gear json
        try:
            file = ''+gear_id+''+'.json'
            f = open(file)
            gear_file = json.load(f)
            shoe_name = gear_file.get('name')
            mile_for_shoe = gear_file.get('converted_distance')
        except:
            new_gear_to_swager(gear_id)
            continue

        if gear_id in db_list:
            continue
        else:
            sql = 'INSERT INTO shoes_miles (gear_id, name, ks) VALUES(?, ?, ?)'
            val = (gear_id, shoe_name, mile_for_shoe)
            with connection:
                cursor.execute(sql,val)




connection.close()
f.close()
