#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import logging.handlers
import time
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
import os
import pandas as pd
import json

logger = logging.getLogger(__name__)


def parse_command_line():
    """Parse command line."""
    arg_parser = argparse.ArgumentParser(
        description="Convert JSON to Excel"
    )
    arg_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable logging at debug level and above",
    )
    arg_parser.add_argument(
        "--log-file",
        default="json_to_excel_conversion.log",
        help="Log file",
    )
    arg_parser.add_argument(
        "--log-file-retention-days",
        type=int,
        default=1,
        help="Log file retention (days)",
    )
    arg_parser.add_argument(
        "--json-file-path",
        required=True,
        help="Path to the JSON file to be converted",
    )
    args = arg_parser.parse_args()
    return args


def setup_logging(args):
    """Configures logging based on command-line arguments."""
    logging.basicConfig(
        format="%(asctime)s  %(levelname)-5s  %(message)s",
        level=logging.DEBUG if args.debug else logging.INFO,
    )
    file_handler = TimedRotatingFileHandler(
        args.log_file, when="midnight", backupCount=args.log_file_retention_days
    )
    file_handler.setFormatter(logging.Formatter("%(asctime)s  %(levelname)-5s  %(message)s"))
    logging.getLogger().addHandler(file_handler)


def read_json_file(json_file_path):
    """Reads the JSON file, validates it, and returns the data."""
    try:
        with open(json_file_path, "r") as file:
            data = json.load(file)
        # Validate that the JSON content is a dictionary or list
        if not isinstance(data, (dict, list)):
            logging.error("Invalid JSON format: Root element must be an object or array.")
            exit(1)
        logging.info("Successfully read and validated JSON file: %s", json_file_path)
        return data
    except FileNotFoundError:
        logging.error("JSON file not found: %s", json_file_path)
        exit(1)
    except json.JSONDecodeError as e:
        logging.error("Failed to parse JSON file: %s. Error: %s", json_file_path, e)
        exit(1)


def save_results_to_excel(data):
    """Converts data to an Excel file and saves it."""
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"output-{timestamp}.xlsx"
    try:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        logging.info("Results successfully saved to: %s", os.path.abspath(filename))
        return os.path.abspath(filename)
    except Exception as e:
        logging.error("Failed to save results to Excel. Error: %s", e)
        exit(1)


def main():
    """Main function to convert JSON to Excel."""
    start_time = time.monotonic()
    args = parse_command_line()
    setup_logging(args)

    if not args.json_file_path:
        logging.error("JSON file path is required")
        exit(1)
    logging.info("Starting conversion of JSON to Excel: %s", args.json_file_path)
    # Read JSON file
    data = read_json_file(args.json_file_path)
    # Save JSON data to Excel
    output_file = save_results_to_excel(data)
    end_time = time.monotonic()
    logging.info(
        "Conversion completed in %.2f seconds. Excel file: %s",
        end_time - start_time,
        output_file,
    )


if __name__ == "__main__":
    main()
