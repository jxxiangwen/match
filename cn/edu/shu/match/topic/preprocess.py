import os.path
import json
import sys

module_path = os.path.abspath(os.path.join(os.getcwd(), os.pardir, os.pardir, os.pardir, os.pardir, os.pardir))
sys.path.append(module_path)
for a_path in sys.path:
    if os.path.exists(os.path.join(a_path, 'cn', 'edu', 'shu', 'match')):
        os.chdir(os.path.join(a_path, 'cn', 'edu', 'shu', 'match'))
        break


def get_config_json(path):
    """
    得到config.json数据
    :param path:
    :return:
    """
    with open(path, encoding='utf-8') as config_file:
        return json.load(config_file)


if __name__ == '__main__':
    pass
