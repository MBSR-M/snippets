#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def version():
    try:
        with open('_version.py', 'r') as file_:
            for line in file_:
                if line.startswith('__version__'):
                    return line.split('=')[1].strip().strip("'")
            raise ValueError("Version string not found in file")
    except (FileNotFoundError, IndexError, ValueError) as e:
        print("Exception occurred:", e)
        return datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')