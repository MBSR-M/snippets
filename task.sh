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

# Fetch the minimum and maximum IDs
min_max_ids=$($mysql --defaults-extra-file=~/.my.cnf -D$PRODDB_NAME -s -N -e "SELECT MIN(id), MAX(id) FROM $SOURCE_TABLENAME;")

# Capture the min_id and max_id
frm_id=$(echo "$min_max_ids" | awk '{print $1}')
to_id=$(echo "$min_max_ids" | awk '{print $2}')

# Check if IDs are fetched properly
if [ -z "$frm_id" ] || [ -z "$to_id" ]; then
    echo "Error: Unable to determine ID range for archival." >> "$STATSLOG"
    exit 1
fi

# Fetch the closest ID <= to_id with UNIX_TIMESTAMP(create_time)
closest_id_info=$($mysql --defaults-extra-file=~/.my.cnf -D$PRODDB_NAME -s -N -e "
    SELECT id, UNIX_TIMESTAMP(create_time)
    FROM $SOURCE_TABLENAME
    WHERE id <= $to_id
    ORDER BY id DESC
    LIMIT 1;
")

# Extract closest ID and timestamp
closest_id=$(echo "$closest_id_info" | awk '{print $1}')
closest_timestamp=$(echo "$closest_id_info" | awk '{print $2}')

# Check if closest ID and timestamp are fetched properly
if [ -z "$closest_id" ] || [ -z "$closest_timestamp" ]; then
    echo "Error: Unable to fetch the closest ID or timestamp." >> "$STATSLOG"
    exit 1
fi

# shellcheck disable=SC2129
echo "Closest ID <= $to_id: $closest_id with timestamp $closest_timestamp" >> "$STATSLOG"
echo "Archiving data with ID range from $frm_id to $closest_id" >> "$STATSLOG"

#################### Archival-script for deletion ##################
# Perform archival and deletion
$Expath --source u=$SOURCEDB_USER,p=$SOURCEDB_PASS,h=$DBHOSTMASTER,P=$SOURCEDB_PORT,D=$PRODDB_NAME,t=$SOURCE_TABLENAME --no-check-charset --purge --where "id >= $frm_id AND id <= $closest_id" --commit-each --limit 12000 --progress 12000 --sleep=4 --statistics --file "$ARCLOG" --why-quit --sentinel "$SENTINEL_LOG" >> "$STATSLOG" 2>&1

# Check if the pt-archiver completed successfully
# shellcheck disable=SC2181
if [ $? -eq 0 ]; then
    echo "Archival completed successfully for $SOURCE_TABLENAME (IDs between $frm_id and $closest_id)." >> "$STATSLOG"
else
    echo "Archival failed for $SOURCE_TABLENAME (IDs between $frm_id and $closest_id)." >> "$STATSLOG"
fi

# End log entry
echo "Archival Process Finished at $(date)" >> "$STATSLOG"