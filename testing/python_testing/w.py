#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime
import configparser
import argparse
from shlex import quote as shlex_quote

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def read_config(config_path):
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
        if 'kafka' not in config:
            raise ValueError("Missing 'Kafka' section in config file.")
        kafka_config = config['kafka']
        return {
            'bootstrap_server': kafka_config.get('bootstrap_server', ''),
            'group': kafka_config.get('topic_group_id', ''),
            'topic': kafka_config.get('topic', '')
        }
    except Exception as e:
        logger.error(f"Error reading config file: {e}")
        exit(1)


def get_datetime(year, month, day):
    time = "00:00:00.000"
    try:
        user_datetime = f"{year}-{month.zfill(2)}-{day.zfill(2)}T{time}"
        datetime.strptime(user_datetime, "%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        logger.error("Invalid date format. Please try again.")
        exit(1)

    return user_datetime


def main():
    current_year = str(datetime.now().year)
    current_month = str(datetime.now().month)
    current_day = str(datetime.now().day)
    parser = argparse.ArgumentParser(description="Kafka Consumer Group Reset")
    parser.add_argument('--config', required=True, help="Path to the Kafka config file")
    parser.add_argument('--year', type=int, default=int(current_year), help="Year (default: current year)")
    parser.add_argument('--month', type=int, default=int(current_month), help="Month (default: current month)")
    parser.add_argument('--day', type=int, default=int(current_day), help="Day (default: current day)")
    args = parser.parse_args()
    config = read_config(args.config)
    user_datetime = get_datetime(str(args.year), str(args.month), str(args.day))
    command = (
        f"./kafka-consumer-groups.sh --bootstrap-server {config['bootstrap_server']} "
        f"--group {config['group']} --topic {config['topic']} "
        f"--reset-offsets --to-datetime {user_datetime} --execute"
    )
    logger.info(f"Executing command: {command}")
    os.system(shlex_quote(command))


if __name__ == "__main__":
    main()
