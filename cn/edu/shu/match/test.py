#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

__author__ = 'jxxia'

# read_algorithm = open('./config/table.json', encoding='utf-8', mode='r')
# json_data = json.load(read_algorithm)  # 加载Json文件
# write_algorithm = open('./config/table.json', encoding='utf-8', mode='w')
# json_data["provide"] = "provide我的"
# json.dump(json_data, write_algorithm, ensure_ascii=False, indent=4, sort_keys=True)


# with open('./result/score.txt', encoding='utf-8', mode='a+') as score_file:
#     score_file.write(str(2.3)+'\n')
#     score_file.writelines(["1","2"] )
#     score_file.write(str(2.3))
with open('./config/genetic.json', encoding='utf-8') as genetic_file:
    genetic_json = json.load(genetic_file)
    with open('./config/algorithm.json', encoding='utf-8') as algorithm_file:
        min = int(['min'])
