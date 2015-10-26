#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jxxia'

import json

with open('./config/table.json', encoding='utf-8') as f:
        table_json = json.load(f)
        print(table_json['require'])

