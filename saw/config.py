# -*- coding: utf-8 -*-

import os
import json

CONFIG_FILEPATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'config.json')
SLACK_URL = ''

with open(CONFIG_FILEPATH) as f:
    config = json.load(f)