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

# Log paths
DATE=$(date '+%m%d%y')
ARCLOG="/opt/backup/ptarchiver_log/archive_log-$SOURCE_TABLENAME-$DATE.log"
STATSLOG="/opt/backup/ptarchiver_log/percona_statistics-$SOURCE_TABLENAME-$DATE.txt"
SENTINEL_LOG="/opt/backup/ptarchiver_log/sentinel-$SOURCE_TABLENAME"

# Date and Time input for archival
echo "Enter the target datetime for archival (YYYY-MM-DD HH:MM:SS):"
read TARGET_DATETIME

# Call Python script to get the closest ID
closest_id=$(python3 find_closest_id.py "$TARGET_DATETIME")
if [ -z "$closest_id" ]; then
    echo "Error: Python script failed to return a valid ID." >> "$STATSLOG"
    exit 1
fi

echo "Closest ID found: $closest_id" >> "$STATSLOG"

# Fetch min_id for archival
frm_id=$(mysql --defaults-extra-file=~/.my.cnf -D$PRODDB_NAME -s -N -e "SELECT MIN(id) FROM $SOURCE_TABLENAME;")
if [ -z "$frm_id" ]; then
    echo "Error: Unable to fetch min_id." >> "$STATSLOG"
    exit 1
fi

# Run pt-archiver
/usr/bin/pt-archiver \
    --source u=$SOURCEDB_USER,p=$SOURCEDB_PASS,h=$DBHOSTMASTER,P=$SOURCEDB_PORT,D=$PRODDB_NAME,t=$SOURCE_TABLENAME \
    --no-check-charset --purge --where "id >= $frm_id AND id <= $closest_id" \
    --commit-each --limit $ARCHIVE_LIMIT --progress $ARCHIVE_LIMIT --sleep=$ARCHIVE_SLEEP \
    --statistics --file "$ARCLOG" --why-quit --sentinel "$SENTINEL_LOG" >> "$STATSLOG" 2>&1

# Check pt-archiver result
if [ $? -eq 0 ]; then
    echo "Archival completed successfully for $SOURCE_TABLENAME (IDs between $frm_id and $closest_id)." >> "$STATSLOG"
else
    echo "Archival failed for $SOURCE_TABLENAME (IDs between $frm_id and $closest_id)." >> "$STATSLOG"
fi

