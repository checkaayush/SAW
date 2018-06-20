# -*- coding: utf-8 -*-

""" Functions helping in tabulating
various AWS resources and their details
"""

import json

import boto3
from terminaltables import AsciiTable
import helpers
import slack
from config import config


def tabularize(table_data):
    """Returns table data as string for tabulation
    
    Args:
        table_data (list): List of rows (lists) of table data
    
    Returns:
        string: String repr of terminaltables.AsciiTable
    """
    return AsciiTable(table_data).table

def images(image_ids=[], **kwargs):
    """Tabulate Amazon Machine Images (AMIs)
    
    Args:
        image_ids (list, optional): List of Image IDs
    """
    client = boto3.client('ec2')
    args = {'Owners': ['self']}
    if 'Filters' in kwargs:
        args['Filters'] = kwargs['Filters']
    if len(image_ids):
        args['ImageIds'] = image_ids
    response = client.describe_images(**args)
    images = response['Images']
    image_attrs = config['image_attributes']
    header = image_attrs
    table_data = [header]
    for image in images:
        row = []
        for key, val in image.iteritems():
            if key in image_attrs:
                row.append(val)
        table_data.append(row)
    if len(table_data) == 1:
        print "\nSorry! No images to show.\n"
    else:
        print tabularize(table_data)

def instances(instance_ids=[], **kwargs):
    """Tabulate EC2 Instances
    
    Args:
        instance_ids (None, optional): List of instance IDs
    """
    client = boto3.client('ec2')
    args = {}
    if 'Filters' in kwargs:
        args['Filters'] = kwargs['Filters']
    if len(instance_ids):
        args['InstanceIds'] = instance_ids
    response = client.describe_instances(**args)
    reservations = response['Reservations']
    instances = []
    for r in reservations:
        instances.extend(r['Instances'])
    header = ['S.No.'] + config['instance_attributes']
    table_data = [header]
    for index, instance in enumerate(instances):
        s_no = str(index + 1)
        row = [s_no]
        for h in header:
            if h == 'Name':
                for t in instance['Tags']:
                    if t['Key'] == 'Name':
                        row.append(t['Value'])
                        break
            elif h == 'Tags':
                tags = helpers.convert_tags_to_string(instance['Tags'])
                row.append(tags)
            elif h == 'State':
                row.append(instance['State']['Name'])        
            elif h in instance.keys():
                row.append(str(instance[h])) 
        table_data.append(row)

    # Show table only when there're data rows in table_data
    if len(table_data) == 1:  # table_data has only header
        print "\nSorry! No instances to show.\n"
    else:
        print tabularize(table_data)

def instance_type(instance_type):
    """Tabulate Instance Type details
    
    Args:
        instance_type (string): Type of EC2 Instance
    """
    headers = ['Resource', 'Specification']
    table_data = [headers]
    details = config['instance_type_details'][instance_type]
    for key, value in details.iteritems():
        table_data.append([key, value])
    print tabularize(table_data)

def elastic_ips():
    """Tabulate Elastic IPs"""
    client = boto3.client('ec2')
    response = client.describe_addresses()
    addrs = response['Addresses']
    header = config['elastic_ip_attributes']
    table_data = [header]
    table_data.extend(helpers.extract_attributes(addrs, header))
    print tabularize(table_data)