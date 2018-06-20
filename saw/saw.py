# -*- coding: utf-8 -*-

"""
saw - Command line utility for AWS EC2 scaffolding and backup.

Usage:
    saw launch --name INSTANCE_NAME ... [--id=IMAGE_ID]
    saw publish --source SOURCE_INSTANCE_NAME --dest DEST_INSTANCE_NAME
    saw backup --id INSTANCE_ID --name IMAGE_NAME [--desc=DESCRIPTION]
    saw images [filter --name=IMAGE_NAME]
    saw instances [filter [--state=INSTANCE_STATE] [--image=IMAGE_NAME] 
                                 [--name=INSTANCE_NAME] [--user=USER]]
    saw elastic_ips
    saw -h | --help

Commands:
    launch                            Launches new EC2 instance(s)  
    publish                           Publish to production from staging instance
    backup                            Create backup AMI Image from EC2 Instance                           
    instances                         Lists all instances in current region
    images                            Lists all images owned by you
    elastic_ips                       Lists all elastic IPs
    filter                            Apply filter on resource

Arguments:
    INSTANCE_NAME                     Name to be assigned to the instance
    SOURCE_INSTANCE_NAME              Name of source instance
    DEST_INSTANCE_NAME                Name of destination instance
    DESCRIPTION                       Description of AWS image
    USER                              Username of creator of the concerned AWS resource
    INSTANCE_ID                       ID of EC2 instance
    INSTANCE_STATE                    Current state of the instance (running | terminated | 
                                      shutting-down | pending | stopping | stopped)
    IMAGE_ID                          Amazon Machine Image ID
    IMAGE_NAME                        Amazon Machine Image Name

Options:
    --name RESOURCE_NAME              AWS Resource Name
    --desc DESCRIPTION                AWS Image Description
    --id RESOURCE_ID                  AWS Resource ID from
    --source SOURCE_INSTANCE_NAME     AWS Instance Name
    --dest DEST_INSTANCE_NAME         AWS Instance Name
    --state INSTANCE_STATE            AWS EC2 Instance State Name
    --image IMAGE_NAME                AMI Name
    --user USER                       User Name
    -h, --help                        Show help message
"""

import os
import sys
import time
import json
import collections

from docopt import docopt
import boto3
from botocore.exceptions import ClientError
from terminaltables import AsciiTable

import tabularize
import helpers
import slack
from config import config
    

def backup(args):
    """Creates AMI (Image) for an EC2 instance.

    Args:
        args (dict): User-supplied command line arguments
    
    Returns:
        ec2.Image: Image resource
    """
    print "Creating backup. This might take upto 5 minutes."
    print "Go, have a cup of coffee and offer one to the developer as well!\n"

    ec2 = boto3.resource('ec2')
    ami_name = args.get('--name')
    if type(ami_name) is list:
        ami_name = ami_name[0]
    desc = args.get('--desc')
    inst_id = args.get('--id')
    instance = ec2.Instance(inst_id)

    new_args = {}
    new_args['Name'] = ami_name
    new_args['Description'] = desc if desc else ''

    image = instance.create_image(**new_args)
    is_available = helpers.poll_image_till_available(image)
    if is_available:
        image.reload()
    return image

def launch_instances(args):
    """Launch EC2 instance(s) from given configuration
    
    Args:
        args (dict): User-supplied command line arguments
    
    Returns:
        list: List of ec2.Instance resources created
    """
    # Use AMI image ID, if supplied
    if args.get('--id'):
        image_id = args.get('--id')
        if image_id:
            config['launch']['ImageId'] = image_id

    # Set number of instances to launch
    i_count = len(args['--name'])
    if i_count > 1:
        config['launch']['MaxCount'] = i_count
    
    # Create instance(s) 
    ec2 = boto3.resource('ec2')
    instances = ec2.create_instances(**config['launch'])

    # Get current user's name to add as tag
    iam = boto3.resource('iam')
    username = iam.CurrentUser().user_name

    for element in zip(instances, args['--name']):
        i = element[0]
        name = element[1]
        # Wait for instance to enter running state
        i.wait_until_running()
        # Reload instance attributes
        i.load()
        # Add Name Tag to instance
        i.create_tags(Tags=[{'Key': 'Name',
                             'Value': name},
                            {'Key': 'User',
                             'Value': username}])
    return instances

def publish(args):
    """Publish to a production instance from staging instance
    Creates an AMI from given source instance and launches the 
    production instance from this AMI

    Args:
        args (dict): User-supplied command line arguments
    
    Returns:
        list: List of production ec2.Instance resources 
    """
    source_inst_name = args.get('--source')
    dest_inst_name = args.get('--dest')
    new_args = {}
    
    # Get current user's name
    iam = boto3.resource('iam')
    username = iam.CurrentUser().user_name

    secs_since_epoch = int(time.time())
    new_args['--name'] = ('BACKUP_' + source_inst_name +
                          '_' + username.upper() + '_' + 
                          str(secs_since_epoch))

    inst_ids = helpers.instance_ids_from_names([source_inst_name])
    if len(inst_ids):
        new_args['--id'] = inst_ids[0]
    else:
        print "No instance found with given source name. Exiting.\n"
        sys.exit()

    # Create AMI from source instance
    try:
        image = backup(new_args)
    except ClientError as e:
        print e
        print "\nExiting.\n"
        sys.exit()

    # Launch Production Instance from this Image
    print "Launching Production Instance...\n"
    instances = launch_instances({'--id': image.image_id,
                                  '--name': [dest_inst_name]})
    
    ## TODO
    # slack.post(instances)
    # slack.post(image(s))
    return instances

def main():
    """Entry point to saw"""
    args = docopt(__doc__)
    # print args

    # Enlist EC2 instances
    if args.get('instances'):
        print "\nInstances\n"
        kwargs = {}
        if args.get('filter'):
            filters = helpers.generate_filters(args)
            kwargs['Filters'] = filters
        tabularize.instances(**kwargs)
    
    # Enlist images (AMIs)
    elif args.get('images'):
        print "\nImages\n"
        kwargs = {}
        if args.get('filter'):
            filters = helpers.generate_filters(args)
            kwargs['Filters'] = filters
        tabularize.images(**kwargs)

    # Enlist Elastic IPs
    elif args.get('elastic_ips'):
        print "\nElastic IPs\n"
        tabularize.elastic_ips()

    # Create Backup (Triggered)
    elif args.get('backup'):
        print "\nBackup\n"
        image = backup(args)
        slack.post(slack.parse(image))
        tabularize.images([image.image_id])

    # Publish to production
    elif args.get('publish'):
        if helpers.confirm_publish():
            print "\nPublishing...\n"
            instances = publish(args)
            
            slack.parse(instances)
            
            tabularize.instances([i.instance_id for i in instances])

    # Confirm and Launch EC2 Instance(s)
    elif args.get('launch'):
        if helpers.confirm_launch():
            print "\nLaunching instance(s)...\n"
            instances = launch_instances(args)
            print "Done.\n"
            tabularize.instances([i.instance_id for i in instances])
            
            slack.parse(instances)

            # Generate PM2 configuration files
            helpers.generate_pm2_config({
                'host': instances[0].public_ip_address
            })

            print "Let's Do This!\n"

if __name__ == '__main__':
    main()
