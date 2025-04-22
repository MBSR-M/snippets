#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import bisect
import datetime
import logging
from typing import Optional, Tuple

log = logging.getLogger(__name__)

# Define EPOCH using the new recommended method
EPOCH = datetime.datetime.fromtimestamp(0, datetime.timezone.utc)


def datetime_to_epoch_seconds(dt: datetime.datetime) -> int:
    """Convert a timezone-aware datetime to epoch seconds."""
    if dt.tzinfo is None:
        raise ValueError('Cannot convert naive datetime to epoch seconds.')
    return int((dt.astimezone(datetime.timezone.utc) - EPOCH).total_seconds())


FIND_ID_LEFT = object()
FIND_ID_RIGHT = object()


def _execute_query(cur, query: str, params: Tuple = ()):
    """Executes a SQL query with error handling."""
    try:
        cur.execute(query, params)
        return cur.fetchall()
    except Exception as e:
        log.error(f"Query failed: {query}, params: {params}, error: {e}")
        raise


def _find_min_max_ids(cur, table_name: str) -> Tuple[Optional[int], Optional[int]]:
    """Retrieve the minimum and maximum IDs from the table."""
    query = f"""
    SELECT MIN(id), MAX(id) FROM {table_name};
    """
    result = _execute_query(cur, query)
    if result:
        return result[0]
    return None, None


def _set_session_timezone(cur, timezone: str = '+0:00'):
    """Set the session timezone to ensure consistent timestamp handling."""
    query = f"SET @@SESSION.time_zone = '{timezone}';"
    _execute_query(cur, query)


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


def find_id(
        cur,
        table_name: str,
        sought_create_time: datetime.datetime,
        bisect_side: object
) -> Optional[int]:
    """
    Find the ID of the record closest to the sought create_time.

    Args:
        cur: Database cursor.
        table_name: Name of the table to query.
        sought_create_time: Target create_time as a datetime object.
        bisect_side: Either FIND_ID_LEFT or FIND_ID_RIGHT to control bisect behavior.

    Returns:
        The ID of the matching record, or None if not found.
    """
    if isinstance(sought_create_time, datetime.datetime):
        sought_create_time = datetime_to_epoch_seconds(sought_create_time)

    # Get min and max IDs in the table
    min_id, max_id = _find_min_max_ids(cur, table_name)
    if min_id is None or max_id is None:
        log.warning("Table is empty or does not exist.")
        return None

    # Set session timezone
    _set_session_timezone(cur)

    # Define a virtual container for lazy fetching of create_time by ID
    class VirtualTuples:
        def __init__(self, min_Id: int, max_Id: int):
            self.min_id = min_Id
            self.max_id = max_Id

        def __len__(self) -> int:
            return self.max_id - self.min_id + 1

        def __getitem__(self, index: int) -> int:
            # Map index to ID in the range [min_id, max_id]
            _id = self.min_id + index
            if _id > self.max_id:
                raise IndexError(f"ID {_id} out of range [{self.min_id}, {self.max_id}].")
            record = _get_record_by_id(cur, table_name, _id)
            if not record:
                raise IndexError(f"ID {_id} not found in table {table_name}.")
            _, create_time = record
            return create_time

    # Perform binary search using the appropriate bisect method
    # Define a virtual container for lazy fetching of create_time by ID
    vt = VirtualTuples(min_id, max_id)
    # Perform binary search using the appropriate bisect method
    bisect_fn = bisect.bisect_right if bisect_side is FIND_ID_RIGHT else bisect.bisect_left
    try:
        # Use binary search on VirtualTuples with index range [0, len(vt))
        found_index = bisect_fn(vt, sought_create_time, 0, len(vt))
        found_id = min_id + found_index if found_index < len(vt) else None
        return found_id
    except Exception as e:
        log.error(f"Error during binary search: {e}")
        return None
