#!/usr/bin/env python

import os

commands = []
commands.append('storage/sqlite/test.py')
commands.append('storage/mysql/test.py')


for command in commands:
    os.system(command)
