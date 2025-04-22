import mysql.connector
from datetime import datetime

# Establish a database connection (replace with your connection parameters)
connection = mysql.connector.connect(
    host="your_host",
    user="your_user",
    password="your_password",
    database="your_database"
)
cur = connection.cursor()

# Set the sought_create_time as a datetime object
sought_create_time = datetime(2025, 1, 20, 12, 0, 0)  # Example datetime

# Specify which bisect side to use (either FIND_ID_LEFT or FIND_ID_RIGHT)
bisect_side = FIND_ID_LEFT  # You can change this depending on your use case

# Call find_id to get the closest ID
record_id = find_id(cur, 'your_table_name', sought_create_time, bisect_side)

# Check the result
if record_id:
    print(f"Found record ID: {record_id}")
else:
    print("Record not found.")

# Close the cursor and connection after use
cur.close()
connection.close()
