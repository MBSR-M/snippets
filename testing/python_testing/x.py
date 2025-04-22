from datetime import timezone, timedelta, datetime
import mysql.connector
import pandas as pd
import pytz
from dateutil import parser
from tzlocal import get_localzone

from snippets.database_config import MySQLConfig
from snippets.database_config.mysql_connector import MySQLConnector

count = 0
exception_list = []

db_args = {
    'host': 'localhost',
    'port': 3306,
    'user': 'admin',
    'password': 'admin',
    'database': 'rtcsyncrep',
    'pool_name': 'rtc-events-pool-01',
    'pool_size': 5,
}
db = MySQLConfig(**db_args)
db_client = MySQLConnector(db)


def ensure_connection():
    """Ensure the MySQL connection is alive."""
    if not db_client.connection.is_connected():
        print("Reconnecting to MySQL...")
        db_client.connect()


def utc_to_local(utc_time):
    """Convert UTC time to local time."""
    if pd.isna(utc_time):
        return None

    if isinstance(utc_time, (datetime, pd.Timestamp)):
        utc_time = utc_time.replace(tzinfo=pytz.UTC)
    elif isinstance(utc_time, str):
        try:
            utc_time = parser.isoparse(utc_time).replace(tzinfo=pytz.UTC)
        except ValueError as e:
            raise ValueError(f"Error parsing timestamp: {e}")
    else:
        raise ValueError(f"Expected a string or datetime, got {type(utc_time)}")

    local_tz = get_localzone()
    local_time = utc_time.astimezone(local_tz)
    return local_time.strftime('%Y-%m-%d %H:%M:%S')


def parse_timestamp(timestamp):
    """Convert a Unix timestamp to a naive datetime object in IST."""
    ist = timezone(timedelta(hours=5, minutes=30))  # IST is UTC+5:30
    return datetime.fromtimestamp(int(timestamp), tz=ist).replace(tzinfo=None)


def insert_rtc_event_data(day_local, msn, node_id, meter_time, nic_time, rtc_drift, text_code,
                          create_time, update_time, event_time):
    try:
        # ensure_connection()  # Ensure the connection is alive
        with db_client._get_cursor() as cursor:
            rtc_event_data_query = f"""
                INSERT INTO rtcsyncrep.rtc_messages (
                    day_local, msn, node_id, meter_time, nic_time, rtc_drift, text_code, create_time, update_time, event_time
                ) VALUES (
                    TO_DAYS('{day_local}'), '{msn}', '{node_id}', '{meter_time}', '{nic_time}', 
                    {rtc_drift}, '{text_code}', '{create_time}', '{create_time}', '{event_time}'
                )
                ON DUPLICATE KEY UPDATE
                    day_local = TO_DAYS('{day_local}'),
                    msn = '{msn}', 
                    node_id = '{node_id}', 
                    meter_time = '{meter_time}', 
                    nic_time = '{nic_time}', 
                    rtc_drift = {rtc_drift}, 
                    text_code = '{text_code}', 
                    create_time = '{create_time}', 
                    update_time = '{create_time}', 
                    event_time = '{event_time}';
            """
            cursor.execute(rtc_event_data_query)
            db_client.connection.commit()
    except mysql.connector.Error as err:
        if err.errno == 2055:  # Cursor is not connected error
            print("Cursor connection lost, retrying...")
            ensure_connection()  # Reconnect
            insert_rtc_event_data(day_local, msn, node_id, meter_time, nic_time, rtc_drift, text_code,
                                  create_time, update_time, event_time)  # Retry the operation
        elif err.errno == 1526:
            print("Partition error: Table has no partition for the provided value.")
        else:
            print(f"Error inserting data, MySQL Error: {err}")
    except Exception as e:
        print(f"Error inserting data for MSN {msn}: {e}")


# Read the Excel file (ensure that headers are present in the file)
df = pd.read_excel(r"C:\Users\MustafaMubashir\Downloads\rtc_data.xlsx")

for index, row in df.iterrows():
    try:
        params_str = str(row[4])
        if pd.isnull(params_str):
            raise ValueError("Column '4' is null.")
        parameters = params_str.split(',')
        if len(parameters) < 3:
            raise ValueError("Not enough parameters in column '4'.")
        event_time = pd.to_datetime(row[7])
        # data = {
        #     'day_local': row[8],
        #     'msn': row[2],
        #     'node_id': row[3],
        #     'meter_time': parse_timestamp(parameters[1]),
        #     'nic_time': parse_timestamp(parameters[0]),
        #     'rtc_drift': int(parameters[2]),
        #     'text_code': row[5],
        #     'create_time': row[6],
        #     'update_time': row[7],
        #     'event_time': row[8],
        # }
        # insert_rtc_event_data(day_local=data['day_local'], msn=data['msn'],
        #                       node_id=data['node_id'], meter_time=data['meter_time'],
        #                       nic_time=data['nic_time'],
        #                       rtc_drift=data['rtc_drift'], text_code=data['text_code'],
        #                       create_time=utc_to_local(data['create_time']),
        #                       update_time=utc_to_local(data['update_time']),
        #                       event_time=utc_to_local(data['event_time']))
        # count += 1
        # print(f"Inserted data for MSN {data['msn']}, count: {count}")
    except Exception as e:
        new_split = str(row[4])
        data = {
            'day_local': row[8],
            'msn': row[2],
            'node_id': row[3],
            'meter_time': parse_timestamp(new_split[10:20]),
            'nic_time': parse_timestamp(new_split[:10]),
            'rtc_drift': new_split[20:],
            'text_code': row[5],
            'create_time': row[6],
            'update_time': row[7],
            'event_time': row[8],
        }
        # insert_rtc_event_data(day_local=data['day_local'], msn=data['msn'],
        #                       node_id=data['node_id'], meter_time=data['meter_time'],
        #                       nic_time=data['nic_time'],
        #                       rtc_drift=data['rtc_drift'], text_code=data['text_code'],
        #                       create_time=utc_to_local(data['create_time']),
        #                       update_time=utc_to_local(data['update_time']),
        #                       event_time=utc_to_local(data['event_time']))
    count += 1
    print(f"Count: {count}")


# TOTAL : 157353