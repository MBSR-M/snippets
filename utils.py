import configparser
import os

currency_code_dict = {
        'PLN': 'EURPLN',
        'CZK': 'EURCZK',
        'SEK': 'EURSEK',
        'DKR': 'EURDKK',
        'HUF': 'EURHUF',
        'RON': 'EURRON'
    }

config = configparser.ConfigParser()
root_path = os.path.dirname(__file__)
path_config = os.path.normpath(os.path.join(root_path, 'path_config.ini'))
config.read(path_config)
mapping_wb_path = config['PATHS']['mapping_sheet_path']
mapping_wb_path_bnl = config['PATHS']['mapping_sheet_path_bnl']
mapping_wb_path_uk = config['PATHS']['mapping_sheet_path_uk']