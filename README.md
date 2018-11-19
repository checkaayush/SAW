# SAW

Command line utility for simple AWS EC2 provisioning and backups

> _Disclaimer: This utility was built in 2016, way before I discovered HashiCorp's excellent tool, [Terraform](https://www.hashicorp.com/products/terraform), which I highly recommend._

## Pre-requisites

- `python 2.7.6`
- `pip`
- AWS Access Key ID, AWS Secret Access Key.

## Installation

- **Step 1:** Run the following command and follow the prompts.
    
    ```sh
    aws configure
    ```
    
    This will ask you for your:
    - *AWS Access Key ID*
    - *AWS Secret Access Key*
    - *Default Region Name (eg.: ap-south-1)*
    - *Default Output Format (Press Enter to choose None)*

    - **References:**
        - [Getting started with AWS CLI](http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html)
        - [AWS EC2 Region Names](http://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region)

- **Step 2:** Install requirements (preferably, in a virtual environment)

    ```sh
    pip install -r requirements.txt
    ```

- **Step 3:** Install *saw* (from project's root directory)
        
    ```sh
    python setup.py install
    ```

## Usage
    
    saw launch --name INSTANCE_NAME ... [--id=IMAGE_ID]
    saw publish --source SOURCE_INSTANCE_NAME --dest DEST_INSTANCE_NAME
    saw backup --id INSTANCE_ID --name IMAGE_NAME [--desc=DESCRIPTION]
    saw images [filter --name=IMAGE_NAME]
    saw instances [filter [--state=INSTANCE_STATE] [--image=IMAGE_NAME] 
                                 [--name=INSTANCE_NAME] [--user=USER]]
    saw elastic_ips
    saw -h | --help

### Commands:

| Command     | Description                                 |
|-------------|---------------------------------------------|
| launch      | Launches new EC2 instance(s)                |
| publish     | Publish to production from staging instance |
| backup      | Create backup AMI Image from EC2 Instance   |
| instances   | Lists all instances in current region       |
| images      | Lists all images owned by you               |
| elastic_ips | Lists all Elastic IPs                       |
| filter      | Apply filter on resource                    |
