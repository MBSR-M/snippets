#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bisect
import datetime
import pymysql
import sys
import logging
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

# Database connection parameters
DB_PARAMS = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "root",
    "database": "sma",
    "port": 3306,
}

SOURCE_TABLENAME = "meter_sample"
FIND_ID_LEFT = object()


def datetime_to_epoch_seconds(dt: datetime.datetime) -> int:
    """Convert a timezone-aware datetime to epoch seconds."""
    if dt.tzinfo is None:
        raise ValueError("Cannot convert naive datetime to epoch seconds.")
    epoch = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)
    return int((dt.astimezone(datetime.timezone.utc) - epoch).total_seconds())


def find_id(cur, table_name: str, sought_create_time: datetime.datetime) -> Optional[int]:
    """Find the closest ID based on the sought datetime."""
    sought_create_time = datetime_to_epoch_seconds(sought_create_time)

    # Get min and max IDs
    cur.execute(f"SELECT MIN(id), MAX(id) FROM {table_name};")
    min_id, max_id = cur.fetchone()
    if min_id is None or max_id is None:
        log.warning("Table is empty or does not exist.")
        return None

    # Create virtual tuples for binary search
    class VirtualTuples:
        def __init__(self, min_id: int, max_id: int):
            self.min_id = min_id
            self.max_id = max_id

        def __len__(self) -> int:
            return self.max_id - self.min_id + 1

        def __getitem__(self, index: int) -> int:
            record_id = self.min_id + index
            cur.execute(f"SELECT id, UNIX_TIMESTAMP(create_time) FROM {table_name} WHERE id = %s;", (record_id,))
            record = cur.fetchone()
            if record:
                return record[1]
            raise IndexError(f"ID {record_id} not found.")

    # Perform binary search
    vt = VirtualTuples(min_id, max_id)
    found_index = bisect.bisect_left(vt, sought_create_time)
    found_id = min_id + found_index if found_index < len(vt) else None
    return found_id


def main():
    if len(sys.argv) != 2:
        log.error("Usage: python3 find_closest_id.py <target_datetime>")
        sys.exit(1)

    try:
        target_datetime = datetime.datetime.strptime(sys.argv[1], "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
    except ValueError:
        log.error("Invalid datetime format. Use YYYY-MM-DD HH:MM:SS.")
        sys.exit(1)

    try:
        conn = pymysql.connect(**DB_PARAMS)
        cur = conn.cursor()

        closest_id = find_id(cur, SOURCE_TABLENAME, target_datetime)
        if closest_id:
            print(closest_id)
        else:
            log.error("No closest ID found.")
            sys.exit(1)

    except Exception as e:
        log.error(f"Database error: {e}")
        sys.exit(1)

    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    main()

