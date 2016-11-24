#!/usr/bin/env python

import os

commands = []
commands.append('storage/SQLite/test.py')
commands.append('storage/MySQL/test.py')
commands.append('storage/test.py')
#commands.append('exchange/test.py')


for command in commands:
    os.system(command)
