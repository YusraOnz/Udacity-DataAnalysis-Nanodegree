#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script is used for creating, filling and querying the database
Ref: https://discussions.udacity.com/t/creating-db-file-from-csv-files-with-non-ascii-unicode-characters/174958/7
"""

import sqlite3
import csv
from pprint import pprint


def drop_table(tableName):
    # drop all the tables before creating any
    cur.execute('DROP TABLE IF EXISTS '+tableName)
    conn.commit()  # save db changes

def query(var,top):

    if top:
        cur.execute('SELECT  value, COUNT(DISTINCT id) as count FROM nodes_tags WHERE key=\''+var+'\' GROUP BY value ORDER BY count DESC LIMIT 7;')
    else:
        cur.execute(var)

    rows = cur.fetchall(var)
    pprint(rows)


#database file name
db_name = 'RiyadhMapDB.db'

# Connect to the database
conn = sqlite3.connect(db_name)

# Get a cursor object
cur = conn.cursor()

drop_table('ways')
drop_table('ways_tags')
drop_table('ways_nodes')
drop_table('nodes')
drop_table('nodes_tags')



#create table: ways
cur.execute("CREATE TABLE ways (id, user, uid, version, changeset, timestamp);")
with open('ways.csv','rt') as file:

    csv_to_list = [(i['id'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) for i in csv.DictReader(file)]

cur.executemany("INSERT INTO ways (id, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?);", csv_to_list)
conn.commit()

#create table: ways_tags
cur.execute("CREATE TABLE ways_tags (id, key, value, type);")
with open('ways_tags.csv','rt') as file:

    csv_to_list = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in csv.DictReader(file)]

cur.executemany("INSERT INTO ways_tags (id, key, value, type) VALUES (?, ?, ?, ?);", csv_to_list)
conn.commit()

#create table: ways_nodes
cur.execute("CREATE TABLE ways_nodes (id, node_id, position);")
with open('ways_nodes.csv','rt') as file:

    csv_to_list = [(i['id'].decode("utf-8"), i['node_id'].decode("utf-8"), i['position'].decode("utf-8")) for i in csv.DictReader(file)]

cur.executemany("INSERT INTO ways_nodes (id, node_id, position) VALUES (?, ?, ?);", csv_to_list)
conn.commit()


# Create table: nodes
cur.execute("CREATE TABLE nodes (id, lat, lon, user, uid, version, changeset, timestamp);")
with open('nodes.csv','rt') as file:
    csv_to_list = [(i['id'].decode("utf-8"), i['lat'].decode("utf-8"), i['lon'].decode("utf-8"), i['user'].decode("utf-8"), i['uid'].decode("utf-8"), i['version'].decode("utf-8"), i['changeset'].decode("utf-8"), i['timestamp'].decode("utf-8")) \
             for i in csv.DictReader(file)]

cur.executemany("INSERT INTO nodes (id, lat, lon, user, uid, version, changeset, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", csv_to_list)
conn.commit()

#create table: nodes_tags
cur.execute("CREATE TABLE nodes_tags (id, key, value, type);")
with open('nodes_tags.csv','rt') as file:

    csv_to_list = [(i['id'].decode("utf-8"), i['key'].decode("utf-8"), i['value'].decode("utf-8"), i['type'].decode("utf-8")) for i in csv.DictReader(file)]

cur.executemany("INSERT INTO nodes_tags (id, key, value, type) VALUES (?, ?, ?, ?);", csv_to_list)
conn.commit()


#---------------------------------------------querying the database--------------------------------------------------

query('SELECT COUNT(*) as total FROM (SELECT user FROM nodes UNION SELECT user FROM ways) ', False)
query('SELECT COUNT(DISTINCT id) FROM nodes;',False)
query('SELECT COUNT(DISTINCT id) FROM ways;',False)


query('amenity',True)

query('cuisine',True)
query('landuse',True)
query('manufacturer',True)
query('religion',True)
query('natural',True)

#close db connection
conn.close()