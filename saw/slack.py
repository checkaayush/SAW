import sys
import json

import requests
import boto3

from config import config, SLACK_URL


def post(payload):
    """Makes POST request to Slack Webhook URL
    
    Args:
        payload (dict/string): Request payload as dict/JSON string 
    
    Returns:
        bool: True for successful request, False otherwise
    """
    if isinstance(payload, dict):
        payload = json.dumps(payload)

    headers = {'Content-Type': 'application/json'}
    try:
        r = requests.post(SLACK_URL,
                          data=payload, 
                          headers=headers)
        
        if r.status_code != 200:
            print "\nFailed to post on Slack. Reason: {}\n".format(r.content)
            return False
        else:
            print "\nSuccessfully posted to Slack.\n"
            return True
    except requests.exceptions.RequestException as e:
        print e
        sys.exit(1)

def parse(data):
    client = boto3.client('ec2')
    
    # If data is instance of ec2.Image
    if str(type(data)) == "<class 'boto3.resources.factory.ec2.Image'>":
        attrs = config['image_attributes']
        image_details = client.describe_images(
                            ImageIds=[data.image_id]
                        )['Images'][0]
        
        # Pick attributes 
        fields = []
        for k, v in image_details.iteritems():
            if k in attrs:
                fields.append({'title': k,
                               'value': v,
                               'short': True})

        # Compose payload
        payload = {}
        payload['title'] = 'saw - Backup created'
        payload['text'] = 'Backup Details'
        payload['fields'] = fields
        return payload

    # If data is collection of ec2.Instances
    elif str(type(data)) == "<class 'boto3.resources.collection.ec2.instancesCollection'>":
        attrs = config['instance_attributes']
        instances = []
        reservations = client.describe_instances(
                            InstanceIds=[i.instance_id for i in data]
                       )['Reservations']
        for r in reservations:
            instances.extend(r['Instances'])

        # Pick attributes
        for i in instances:
            fields = []
            for attr in attrs:
                if attr == 'State':
                    v = i[attr]['Name']
                elif attr == 'Name':
                    v = [t['Value'] for t in i['Tags'] if t['Key'] == 'Name'][0]
                else:
                    v = i[attr]
                fields.append({
                              'title': attr,
                              'value': v,
                              'short': True})

            # Compose payload 
            payload = {}
            payload['text'] = "saw - Instances launched/published"
            payload['fields'] = fields
            # print json.dumps(payload, indent=2)

            # Post to Slack
            post(payload)

    return {}

