""" Common helper functions 

Attributes:
    CONFIG_FILEPATH (os.path): Path to 
        configuration file (config.json)
"""

import os
import json
import time
from collections import OrderedDict

import boto3

import tabularize
from config import config


def allocate_elastic_ip():
    """Allocate a new standard Elastic IP for default region
    
    Returns:
        string: Public Elastic IP address allocated
    """
    client = boto3.client('ec2')
    response = client.allocate_address(Domain='standard')
    return response['PublicIp']

def associate_elastic_ip(elastic_ip, instance_id):
    """Associate given Elastic IP address with instance 
    
    Args:
        elastic_ip (string): Elastic IP address
        instance_id (string): ID of instance
    
    Returns:
        bool: Success/Failure of the association
    """
    client = boto3.client('ec2')
    response = client.associate_address(
        InstanceId=instance_id,
        PublicIp=elastic_ip
    )
    return bool(response['AssociationId'])

def confirm_launch():
    """Confirm launch of instance(s) from user
    
    Returns:
        bool: Launch confirmed or not
    """
    print "\nAbout to launch instance(s) with following configuration:\n"
    instance_type = config['launch']['InstanceType']
    details = config['instance_type_details'][instance_type]
    tabularize.instance_type(config['launch']['InstanceType'])
    choice = raw_input('\nAre you sure?: ([y]/n) ') or 'y'
    return (choice == 'y' or choice == 'Y')

def confirm_publish():
    """Ask for confirmation before publishing"""
    choice = raw_input("\nAre you sure you want to publish?: ([y]/n) ") or 'y'
    return (choice == 'y' or choice == 'Y')

def sanitize_headers(headers):
    """Reformat column headers for tabulation
    
    Args:
        headers (list): Column headers
    
    Returns:
        list: List of sanitized column headers 
    """
    sanitized_headers = []
    for header in headers:
        h = ' '.join(header.split('_'))
        sanitized_headers.append(h.title())
    return sanitized_headers

def compose_public_dns_name(instance):
    """Compose Public DNS Name from instance attributes
    
    Args:
        instance (ec2.Instance): ec2.Instance object
    
    Returns:
        string: Public DNS Name
    """
    ip = '-'.join(instance.public_ip_address.split('.'))
    # Exclude zone identifier from availability zone for region
    region = instance.placement['AvailabilityZone'][:-1]
    subdomain = "compute.amazonaws.com"
    return "ec2-{ip}.{region}.{subdomain}".format(ip=ip,
                                                  region=region,
                                                  subdomain=subdomain)

def convert_tags_to_string(tags):
    """Convert Tags (key-value pairs) to string for tabulation 
    
    Args:
        tags (list): List of tag key-value pairs
    
    Returns:
        string: String formed by concatenating tags
    """
    tag_str = ''
    temp_tags = []
    for tag in tags:
        temp_tags.append("{key} = {value}".format(key=tag['Key'],
                                                  value=tag['Value']))
    return ', '.join(temp_tags)

def extract_attributes(details, req_attrs):
    """Extract required attribute values from resource details
    
    Args:
        details (list): List of dicts of resource details
        req_attrs (list): Attributes to be extracted
    
    Returns:
        list: List of rows with resource attribute values
    """
    rows = []
    for d in details:
        row = []
        for attr in req_attrs:
            val = d.get(attr)
            val = val if val else ''
            row.append(val)
        rows.append(row)
    return rows

def generate_pm2_config(args):
    """Generates PM2 configuration files
    
    Args:
        args (dict): Configuration parameters
    """
    def write_to_file(filepath, content_dict):
        with open(filepath, 'w') as f:
            f.write(json.dumps(content_dict,
                               indent=2))

    def create_config_file(repo_type):
        content_dict = config['pm2'][repo_type]
        params = content_dict['deploy']['push']
        params['host'] = host
        params['ref'] = ref
        if repo_type == 'backend':
            params['repo'] = backend_repo
            params['path'] = backend_path
        else:
            params['repo'] = frontend_repo
            params['path'] = frontend_path
        filename = 'pm2_' + repo_type + '.json'
        filepath = os.path.join(os.getcwd(),
                                filename)
        write_to_file(filepath, content_dict) 
        print "Created {f} in current directory.\n".format(f=filename)
    
    print "\nPM2 configuration file details:"
    
    ## TODO: Too much hard-coded stuff. Have scope to change environment, user, etc.
    # Defaults 
    default_backend_repo = config['pm2']['backend']['deploy']['push']['repo']
    default_frontend_repo = config['pm2']['frontend']['deploy']['push']['repo']
    default_backend_path = config['pm2']['backend']['deploy']['push']['path']
    default_frontend_path = config['pm2']['frontend']['deploy']['push']['path']
    default_branch = config['pm2']['frontend']['deploy']['push']['ref']

    backend_repo = raw_input('\nEnter Backend Repo URL: ["{}"] '.format(default_backend_repo)) or default_backend_repo
    frontend_repo = raw_input('Enter Frontend Repo URL: ["{}"] '.format(default_frontend_repo)) or default_frontend_repo
    ref = raw_input('Enter Branch name: ["{}"]) '.format(default_branch)) or default_branch
    host = args['host']
    backend_path = (raw_input('Enter Backend Path on server: ["{}"] '.format(default_backend_path)) or
                    default_backend_path)
    frontend_path = (raw_input('Enter Frontend Path on server: ["{}"] '.format(default_frontend_path)) or
                    default_frontend_path)
    print
    create_config_file('backend')
    create_config_file('frontend')

def image_ids_from_names(image_names):
    """Get Image IDs from given Image Names
    
    Args:
        image_names (list): List of Image Names
    
    Returns:
        list: List of Image IDs
    """
    ec2 = boto3.resource('ec2')
    images = ec2.images.filter(Filters=[{
        'Name': 'name',
        'Values': image_names
    }])
    return [i.image_id for i in images]

def instance_ids_from_names(inst_names):
    """Get Instance IDs from Instance Names
    
    Args:
        inst_names (list): List of Instance Names
    
    Returns:
        list: List of Instance IDs
    """
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{
        'Name': 'tag-value',
        'Values': inst_names
    }])
    return [i.instance_id for i in instances]

def instance_names_from_ids(inst_ids):
    """Return Instance names from given Instance IDs
    
    Args:
        inst_ids (list): List of Instance IDs
    
    Returns:
        list: List of Instance Names
    """
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(
                    Filters=[{
                        'Name': 'instance-id',
                        'Values': inst_ids
                }])
    inst_names = []
    for i in instances:
        for t in i.tags:
            if 'Key' == 'Name':
                inst_names.append(t['Value'])
    return inst_names

def poll_image_till_available(image):
    """Poll for image to be 'available'
    
    Args:
        image (ec2.Image): Image to poll 
    
    Returns:
        bool: True if Image available, False otherwise
    """
    # print "Waiting for image state to be 'available'..."
    # print "\nIt might take upto 5 minutes. Please wait...\n"
    
    start_time = time.time()
    while True:
        status = image.state
        if status == "available":
            # print "\nCreated Image is now 'available'.\n"
            return True
        else:
            if (time.time() - start_time) > 300:
                print "\nWaited for ~5 minutes. Backup image creation failed.\n"
                return False
            time.sleep(15)
            image.reload()
            continue

def generate_filters(args):
    """Generate Filters from command line arguments
    
    Args:
        args (dict): Command line arguments parsed using Docopt
    
    Returns:
        list: List of filters as key-value pairs. Empty list for insufficent data.
    """
    def compose_filters(name, values):
        return [{
            'Name': name,
            'Values': values
        }]

    # AMI Image Filters
    if args.get('images'):
        if args.get('--name'):
            name = 'name'
            values = args.get('--name')
            return compose_filters(name, values)
        else:
            return []

    # EC2 Instance Filters
    if args.get('instances'):
        filters = []

        # Filter: Instance State Name (running, pending, etc.)
        if args.get('--state'):
            name = 'instance-state-name'
            values = [args.get('--state')]
            filters.extend(compose_filters(name, values))
        
        # Filter: Image ID (from supplied Image name)
        if args.get('--image'):
            name = 'image-id'
            values = image_ids_from_names([args.get('--image')])
            filters.extend(compose_filters(name, values))
        
        # Filter: Supplied name against tag values (independent of key)
        if args.get('--name'):
            name = 'tag-value'
            values = args.get('--name')
            filters.extend(compose_filters(name, values))
        
        # Filter: Supplied user name against tag values
        if args.get('--user'):
            name = 'tag-value'
            values = [args.get('--user')]
            filters.extend(compose_filters(name, values))

        # Return final list of filters
        return filters

    return []
