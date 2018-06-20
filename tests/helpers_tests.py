import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import boto3
from nose.tools import *

from saw import helpers

instance_id = ''
ec2 = boto3.resource('ec2')
instance = ec2.Instance(instance_id)

def test_generate_pm2_config():
    helpers.generate_pm2_config({'host': '192.168.0.1'})

def test_confirm_launch():
    assert_true(helpers.confirm_launch())

def test_compose_public_dns_name():
    fn_dns_name = helpers.compose_public_dns_name(instance)
    fn_region = fn_dns_name.split('.')[1]
    fn_ip = '.'.join(fn_dns_name.split('.')[0].split('-')[1:])

    dns_name = instance.public_dns_name
    region = instance.placement['AvailabilityZone'][:-1]
    ip = instance.public_ip_address

    assert_equal(fn_dns_name, dns_name)
    assert_equal(fn_region, region)
    assert_equal(fn_ip, ip)

