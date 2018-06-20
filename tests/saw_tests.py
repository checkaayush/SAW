import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import json
import boto3
from nose.tools import *

from saw import saw, helpers, tabularize

CONFIG_FILEPATH = '/home/aayush/Desktop/saw/saw/config.json'

def test_launch_instance():
    if helpers.confirm_launch():
        i = saw.launch_instances({'--name': 'TESTS'})
        tabularize.instances(i)
