#!/bin/bash

# Ensure the log directories exist
LOG_DIR="/opt/backup/ptarchiver_log"
mkdir -p "$LOG_DIR"

# Define variables
DBHOSTMASTER='127.0.0.1'
SOURCEDB_USER='root'
SOURCEDB_PASS='root'
SOURCEDB_PORT='3306'
PRODDB_NAME='sma'
SOURCE_TABLENAME='meter_sample'

# Log paths
DATE=$(date '+%m%d%y')
ARCLOG="$LOG_DIR/archive_log-$SOURCE_TABLENAME-$DATE.log"
STATSLOG="$LOG_DIR/percona_statistics-$SOURCE_TABLENAME-$DATE.txt"
SENTINEL_LOG="$LOG_DIR/sentinel-$SOURCE_TABLENAME"

# Automatically calculate the target datetime: current day - 180 days
TARGET_DATETIME=$(date -d 'now - 180 days' '+%Y-%m-%d %H:%M:%S')
echo "Automatically calculated target datetime: $TARGET_DATETIME"

# Convert target datetime to UNIX timestamp
TARGET_TIMESTAMP=$(date -d "$TARGET_DATETIME" +"%s")
if [ $? -ne 0 ]; then
    echo "Error: Unable to calculate target timestamp. Exiting..." >> "$STATSLOG"
    exit 1
fi

# Fetch the minimum and maximum IDs
min_max_ids=$(mysql --defaults-extra-file=~/.my.cnf -D$PRODDB_NAME -s -N -e "SELECT MIN(id), MAX(id) FROM $SOURCE_TABLENAME;")
frm_id=$(echo "$min_max_ids" | awk '{print $1}')
to_id=$(echo "$min_max_ids" | awk '{print $2}')

# Check if IDs are fetched properly
if [ -z "$frm_id" ] || [ -z "$to_id" ]; then
    echo "Error: Unable to determine ID range for archival." >> "$STATSLOG"
    exit 1
fi

# Use external script to find the closest ID
closest_id=$(./find-meter-sample-by-create-time.sh "$TARGET_TIMESTAMP" | awk '/Found at id/ {print $4}')

# Check if the closest ID was found
if [ -z "$closest_id" ]; then
    echo "Error: Unable to fetch the closest ID." >> "$STATSLOG"
    exit 1
fi

echo "Closest ID found: $closest_id" >> "$STATSLOG"

# Run pt-archiver for archival
/usr/bin/pt-archiver \
    --source u=$SOURCEDB_USER,p=$SOURCEDB_PASS,h=$DBHOSTMASTER,P=$SOURCEDB_PORT,D=$PRODDB_NAME,t=$SOURCE_TABLENAME \
    --no-check-charset --purge --where "id >= $frm_id AND id <= $closest_id" \
    --commit-each --limit 12000 --progress 12000 --sleep=4 \
    --statistics --file "$ARCLOG" --why-quit --sentinel "$SENTINEL_LOG" >> "$STATSLOG" 2>&1

# Check if the archival was successful
# shellcheck disable=SC2181
if [ $? -eq 0 ]; then
    echo "Archival completed successfully for $SOURCE_TABLENAME (IDs between $frm_id and $closest_id)." >> "$STATSLOG"
else
    echo "Archival failed for $SOURCE_TABLENAME (IDs between $frm_id and $closest_id)." >> "$STATSLOG"
    exit 1
fi