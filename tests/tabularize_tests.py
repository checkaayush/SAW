import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import boto3
from nose.tools import *

from saw import tabularize


def test_tabularize():
    tabularize.tabularize([
        ['Name', 'Age'],
        ['John', '21']
    ])

def test_images():
    tabularize.images()

def test_instances():
    tabularize.instances()
