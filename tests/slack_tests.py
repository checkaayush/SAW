import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import json
import boto3
from nose.tools import *

from saw import slack, helpers, tabularize

def test_parse():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{
                                        'Name': 'tag-value',
                                        'Values': ['NITI_DASHBOARD']
                                    }])
    # tabularize.instances([i.instance_id for i in instances])
    slack.parse(instances)
    # image = ec2.Image('ami-16c9a379')  # DASHBOARD_STARTER
    # parsed = slack.parse(image)
    # print parsed
    # slack.post(parsed)

