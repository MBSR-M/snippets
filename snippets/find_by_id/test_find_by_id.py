#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import mysql.connector
from datetime import datetime, timezone

from snippets.find_by_id import find_id, FIND_ID_LEFT, FIND_ID_RIGHT

connection = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="admin",
    database="rtcsyncrep"
)
cur = connection.cursor()

sought_create_time = datetime(2024, 9, 8, 0, 0, 0, tzinfo=timezone.utc)
bisect_side = FIND_ID_LEFT
record_id = find_id(cur, 'device_events', sought_create_time, bisect_side)

if record_id:
    print(f"Found record ID: {record_id}")
else:
    print("Record not found.")

# Close the cursor and connection after use
cur.close()
connection.close()
