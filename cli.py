import json
import os
import sys
import time

import click
from loguru import logger

from src.process import upload_all_files, upload_all_files_mef

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--json_path", "-j", help="json file path", type=click.Path(exists=True))
def cli(json_path):
    start_time = time.monotonic()
    logger.remove()  # reset
    logger.add(sys.stderr, colorize=True, level="INFO",
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green>|<level>{message}</level>")  # add new format for info
    logger.add(sys.stderr, colorize=True, level="ERROR",
               format="<red>{time:YYYY-MM-DD HH:mm:ss}</red>|<level>{message}</level>")  # add new format for info

    logger.info(f"{json_path=}")
    with open(json_path) as f:
        data = json.loads(f.read())
    time_stamp = data["trigger_timestamp"]
    trigger_button = data['trigger_button']
    root_folder = data["prod_root_folder"]
    country = data['country_code']
    forex_file_name = data["forex_rate_file"]
    mef_file_name = data["mef_file"]
    input_file_folder_name = 'inputs'
    forex_file_path = f"{root_folder}\{input_file_folder_name}\{forex_file_name}"
    mef_file_path = os.path.join(root_folder, input_file_folder_name, mef_file_name)
    logger.info(f"mef file path {mef_file_path}")
    output_path = os.path.join(root_folder, 'outputs')
    logger.info(f"output file :: {output_path}")

    if trigger_button == 'mef_file':
        items = []
        for key, json_data in data['plants'].items():
            if country == 'BNL' or country == 'UK':
                input_folder = os.path.join(root_folder, input_file_folder_name)
                dict_resp = {'input_folder': input_folder, 'code': key, 'items': json_data}
                items.append(dict_resp)
            elif 'input_file' in json_data and json_data['input_file'].endswith(('.xlsx', '.xls', '.csv', '.txt')):
                input_file = os.path.join(root_folder, input_file_folder_name, json_data['input_file'])
                dict_resp = {'input_file': input_file, 'code': key,
                             'input_received_date': json_data['input_received_date']}
                items.append(dict_resp)
            elif 'input_file' in json_data and not json_data['input_file'].endswith(('.xlsx', '.xls', '.csv', '.txt')):
                dict_resp = {'code': key,
                             'input_received_date': json_data['input_received_date'],
                             'interval': json_data['select_field']}
                items.append(dict_resp)


        upload_all_files_mef(mef_file_path, country, items, output_path, forex=forex_file_path)
        logger.info('MEF sheet generated successfully')
    else:
        for key, json_data in data['plants'].items():
            input_file = os.path.join(root_folder, input_file_folder_name, json_data['input_file'])
            upload_all_files(input_file=input_file, forex=forex_file_path, country=country, plant=key,
                             date=json_data['input_received_date'], output_path=output_path)
    end_time = time.monotonic()
    logger.info(f"Total time taken: {round((end_time - start_time), 2)} seconds")


if __name__ == '__main__':
    cli()

