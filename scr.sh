#!/bin/bash

# Ensure the log directories exist
mkdir -p /opt/backup/ptarchiver_log

# Define variables
DBHOSTMASTER='127.0.0.1'
SOURCEDB_USER='root'
SOURCEDB_PASS='root'
SOURCEDB_PORT='3306'
PRODDB_NAME='sma'
SOURCE_TABLENAME='meter_sample'

# Date for log filenames
DATE=$(date '+%m%d%y')
ARCLOG="/opt/backup/ptarchiver_log/archive_log-$SOURCE_TABLENAME-$DATE.log"
Expath='/usr/bin/pt-archiver'
mysql='/usr/bin/mysql'

# Log paths
DATELOG="/opt/backup/ptarchiver_log/DateData-$SOURCE_TABLENAME.txt"
STATSLOG="/opt/backup/ptarchiver_log/percona_statistics-$SOURCE_TABLENAME-$DATE.txt"
SENTINEL_LOG="/opt/backup/ptarchiver_log/sentinel-$SOURCE_TABLENAME"

# Log start time
echo "Archival Process Started at $(date)" >> "$DATELOG"
sleep 2

# Get current timestamp from DB using secure login
Now_Date=$($mysql --defaults-extra-file=~/.my.cnf -D$PRODDB_NAME -s -N -e "SELECT NOW();")
echo "Current Date and Time from DB: $Now_Date" >> "$STATSLOG"

# Fetch dynamic range of IDs to be archived using Python
min_max_ids=$(python3 - <<EOF
import mysql.connector
import datetime
from typing import Optional, Tuple

# Your functions here
def _execute_query(cur, query: str, params: Tuple = ()):
    try:
        cur.execute(query, params)
        return cur.fetchall()
    except Exception as e:
        raise Exception(f"Query failed: {query}, params: {params}, error: {e}")

def _find_min_max_ids(cur, table_name: str) -> Tuple[Optional[int], Optional[int]]:
    query = f"SELECT MIN(id), MAX(id) FROM {table_name};"
    result = _execute_query(cur, query)
    if result:
        return result[0]
    return None, None

def _get_record_by_id(cur, table_name: str, _id: int) -> Optional[Tuple[int, int]]:
    """Fetch the record with the closest ID <= _id."""
    query = (
        f"""
        SELECT id, UNIX_TIMESTAMP(create_time) FROM {table_name}
        WHERE id <= %s ORDER BY id DESC LIMIT 1;
        """
    )
    result = _execute_query(cur, query, (_id,))
    return result[0] if result else None

# Connect to MySQL database
db_connection = mysql.connector.connect(
    host="$DBHOSTMASTER",
    user="$SOURCEDB_USER",
    password="$SOURCEDB_PASS",
    database="$PRODDB_NAME"
)

cursor = db_connection.cursor()

# Fetch min and max IDs
min_id, max_id = _find_min_max_ids(cursor, "$SOURCE_TABLENAME")

cursor.close()
db_connection.close()

# Output the result
print(min_id, max_id)
EOF
)

# Capture the min_id and max_id from the Python script output
frm_id=$(echo "$min_max_ids" | awk '{print $1}')
to_id=$(echo "$min_max_ids" | awk '{print $2}')

# Check if IDs are fetched properly
if [ -z "$frm_id" ] || [ -z "$to_id" ]; then
    echo "Error: Unable to determine ID range for archival." >> "$STATSLOG"
    exit 1
fi
echo "Archiving data with ID range from $frm_id to $to_id" >> "$STATSLOG"

#################### Archival-script for deletion ##################
# Perform archival and deletion
$Expath --source u=$SOURCEDB_USER,p=$SOURCEDB_PASS,h=$DBHOSTMASTER,P=$SOURCEDB_PORT,D=$PRODDB_NAME,t=$SOURCE_TABLENAME --no-check-charset --purge --where "id >= $frm_id AND id <= $to_id" --commit-each --limit 12000 --progress 12000 --sleep=4 --statistics --file "$ARCLOG" --why-quit --sentinel "$SENTINEL_LOG" >> "$STATSLOG" 2>&1

# Check if the pt-archiver completed successfully
# shellcheck disable=SC2181
if [ $? -eq 0 ]; then
    echo "Archival completed successfully for $SOURCE_TABLENAME (IDs between $frm_id and $to_id)." >> "$STATSLOG"
else
    echo "Archival failed for $SOURCE_TABLENAME (IDs between $frm_id and $to_id)." >> "$STATSLOG"
fi

# End log entry
echo "Archival Process Finished at $(date)" >> "$STATSLOG"
