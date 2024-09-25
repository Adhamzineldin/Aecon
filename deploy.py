import boto3
import time
from botocore.exceptions import ClientError
import time
import mysql.connector

region = 'eu-north-1'
# Initialize boto3 clients
ec2_client = boto3.client('ec2', region_name=region)
s3_client = boto3.client('s3', region_name=region)
rds_client = boto3.client('rds', region_name=region)
ec2_resource = boto3.resource('ec2', region_name=region)

# Name of the EC2 instance
instance_name = 'Aceon5'  # Update with your desired instance name
rds_db_instance_id = 'Aceon-Django-DB'

# 1. Create an EC2 Instance for Django App or update existing one
def create_or_update_ec2_instance(security_group_id, db_url):
    try:
        # Check for existing instances with the specified name
        instances = ec2_resource.instances.filter(Filters=[{'Name': 'tag:Name', 'Values': [instance_name]}])
        existing_instance = next(iter(instances), None)

        if existing_instance:
            print(f"Found existing instance: {existing_instance.id}. Updating files...")
            instance_id = existing_instance.id

            # Optionally, you can execute commands on the existing instance here
            # e.g., using Systems Manager or SSH
            update_instance_files(instance_id)

            existing_instance.reload()
            public_ip = existing_instance.public_ip_address
            public_dns = existing_instance.public_dns_name

            print(f"Your website should be accessible at: http://{public_ip} or http://{public_dns}")
            return instance_id
        else:
            print("Creating new EC2 instance...")
            user_data_script = '''#!/bin/bash
            # Update package index
            sudo apt update || { echo "Failed to update package index"; exit 1; }

            # Install Python 3.12 and necessary packages
            sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip libpq-dev postgresql postgresql-contrib nginx curl git || { echo "Failed to install required packages"; exit 1; }

            # Create a directory for the Django app
            APP_DIR="/home/ubuntu/mydjangoapp"
            sudo mkdir -p $APP_DIR || { echo "Failed to create app directory"; exit 1; }

            # Clone your Django app from your repository
            git clone https://github.com/Adhamzineldin/Aecon.git $APP_DIR || { echo "Failed to clone repository"; exit 1; }

            # Navigate to the application directory
            cd $APP_DIR || { echo "Failed to navigate to app directory"; exit 1; }

            # Create a virtual environment using Python 3.12
            /usr/bin/python3.12 -m venv venv || { echo "Failed to create virtual environment"; exit 1; }

            # Activate the virtual environment
            source venv/bin/activate

            # Upgrade pip and install dependencies from requirements.txt
            pip install --upgrade pip || { echo "Failed to upgrade pip"; exit 1; }
            pip install -r serverReq.txt || { echo "Failed to install dependencies"; exit 1; }

           
            # Set environment variables for Django (only for the current session)
            export DBNAME="aecon"
            export DBHOST="aceon-django-db.cruwmaqss4p9.eu-north-1.rds.amazonaws.com"
            export DBUSER="admin"
            export DBPASS="a251m2006"
            export DBPORT="3306"
            export SECRET_KEY="h6#9_tw1#cc_q7*da(1=ni(-%t45wx)qvlyx+c6wt7+5)aqk0r"
            export API_KEY="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"
            export DEBUG=True
            export WEBSITE_HOSTNAME="127.0.0.1"
            export SEND_MAIL_TO="sam.aziz@tracsis.com"

            # Run Django commands with error handling
            python manage.py migrate || { echo "Failed to run migrations"; exit 1; }
            
            # fixes a bug
            sudo chmod -R 777 /home/ubuntu/mydjangoapp/aecon/static/media/temp_data/processing
            
            #run server
            python manage.py runserver 0.0.0.0:8000 || { echo "Failed to run server"; exit 1; }
        
            '''

            instance = ec2_resource.create_instances(
                ImageId='ami-04cdc91e49cb06165',  # Replace with an appropriate AMI ID for your region
                InstanceType='t3.micro',  # Free tier instance type
                MinCount=1,
                MaxCount=1,
                SecurityGroupIds=[security_group_id],
                UserData=user_data_script,
                TagSpecifications=[{
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': instance_name}]
                }]
            )
            instance_id = instance[0].id
            print(f"EC2 instance {instance_id} created.")
            instance[0].wait_until_running()
            print(f"EC2 instance {instance_id} is running.")

            # Refresh instance data to retrieve the public IP/DNS
            instance[0].reload()
            public_ip = instance[0].public_ip_address
            public_dns = instance[0].public_dns_name

            print(f"Your website should be accessible at: http://{public_ip} or http://{public_dns}")

            return instance_id
    except Exception as e:
        print(f"Error creating or updating EC2 instance: {e}")

# 2. Update existing instance files (placeholder for actual file update logic)
def update_instance_files(instance_id):
    print(f"Updating files on instance {instance_id}...")

    # You can implement file update logic here, possibly using SSH or AWS Systems Manager
    # For example, you might want to SSH into the instance and pull the latest code from your repository.
    # If you are using Systems Manager, you can execute commands directly.

# 3. Create an S3 Bucket for Static/Media Files
def create_s3_bucket(bucket_name):
    try:
        print(f"Creating S3 bucket: {bucket_name}...")
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': 'eu-north-1'}  # Specify your region
        )
        print(f"S3 bucket {bucket_name} created.")
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            print(f"Bucket {bucket_name} already exists and is owned by you.")
        else:
            print(f"Error creating S3 bucket: {e}")

# 4. Create an RDS instance for the Database (PostgreSQL)
def create_rds_instance(db_instance_id, db_name, username, password, region, sql_file_path):
    # Create a security group for the RDS instance if it doesn't exist
    security_group_id = create_security_group()
    if not security_group_id:
        print("Failed to create or retrieve security group.")
        return None

    try:
        # Check if the RDS instance already exists
        rds_instances = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
        if rds_instances['DBInstances']:
            print(f"RDS instance {db_instance_id} already exists. Retrieving connection details...")
            # Retrieve the actual endpoint from the existing instance
            endpoint = rds_instances['DBInstances'][0]['Endpoint']['Address']
            return f"mysql://{username}:{password}@{endpoint}:3306/{db_name}"
    except ClientError as e:
        if e.response['Error']['Code'] != 'DBInstanceNotFound':
            print(f"Error checking for RDS instance: {e}")
            return None

    try:
        print(f"Creating RDS instance: {db_instance_id}...")
        rds_client.create_db_instance(
            DBInstanceIdentifier=db_instance_id,
            AllocatedStorage=20,
            DBInstanceClass='db.t3.micro',  # Instance type
            Engine='mysql',
            MasterUsername=username,
            MasterUserPassword=password,
            DBName=db_name,
            BackupRetentionPeriod=7,  # Keep backups for 7 days
            MultiAZ=False,  # Single AZ deployment for free tier
            PubliclyAccessible=True,
            VpcSecurityGroupIds=[security_group_id]  # Attach the security group to the RDS instance
        )
        print(f"RDS instance {db_instance_id} is being created.")

        # Wait until the instance is available
        while True:
            response = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
            status = response['DBInstances'][0]['DBInstanceStatus']
            print(f"Current status: {status}")
            if status == 'available':
                print(f"RDS instance {db_instance_id} is now available.")
                break
            elif status in ['failed', 'deleting']:
                print(f"RDS instance {db_instance_id} is in an unexpected state: {status}.")
                return None
            time.sleep(30)  # Check status every 30 seconds

        # Retrieve the actual endpoint after the instance is available
        endpoint = response['DBInstances'][0]['Endpoint']['Address']

        # Connect to the MySQL instance and upload the default database
        conn = mysql.connector.connect(
            host=endpoint,
            user=username,
            password=password,
            database=db_name
        )

        cursor = conn.cursor()

        # Read the SQL file and execute it
        with open(sql_file_path, 'r') as sql_file:
            sql_script = sql_file.read()
            for statement in sql_script.split(';'):
                if statement.strip():
                    cursor.execute(statement)

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Default database uploaded to RDS instance {db_instance_id}.")
        return f"mysql://{username}:{password}@{endpoint}:3306/{db_name}"

    except Exception as e:
        print(f"Error creating RDS instance or uploading database: {e}")
        return None


# 5. Create a Security Group with Inbound Rules
def create_security_group():
    try:
        print("Creating Security Group...")
        response = ec2_client.create_security_group(
            GroupName='django-sg',
            Description='Security group for Django app'
        )
        security_group_id = response['GroupId']
        print(f"Security Group {security_group_id} created.")

        # Add rules to allow HTTP, HTTPS, and SSH
        ec2_client.authorize_security_group_ingress(
            GroupId=security_group_id,
            IpPermissions=[
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 22,
                    'ToPort': 22,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 80,
                    'ToPort': 80,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 443,
                    'ToPort': 443,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                },
                {
                    'IpProtocol': 'tcp',
                    'FromPort': 8000,
                    'ToPort': 8000,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Allow requests on port 8000
                },{
                    'IpProtocol': 'tcp',
                    'FromPort': 3306,
                    'ToPort': 3306,
                    'IpRanges': [{'CidrIp': '0.0.0.0/0'}]  # Allow requests on port 8000
                }
            ]
        )
        return security_group_id
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
            print("Security group 'django-sg' already exists. Retrieving its ID...")
            # Retrieve the existing security group ID
            response = ec2_client.describe_security_groups(GroupNames=['django-sg'])
            return response['SecurityGroups'][0]['GroupId']
        else:
            print(f"Error creating security group: {e}")

# 6. Create a CORS policy for S3 bucket (Optional)
def add_s3_cors_policy(bucket_name):
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedHeaders': ['Authorization'],
                'AllowedMethods': ['GET', 'PUT'],
                'AllowedOrigins': ['*'],
                'ExposeHeaders': ['GET', 'PUT'],
                'MaxAgeSeconds': 3000
            }
        ]
    }
    try:
        print(f"Adding CORS policy to bucket: {bucket_name}...")
        s3_client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration=cors_configuration)
        print("CORS policy added.")
    except Exception as e:
        print(f"Error adding CORS policy: {e}")

# Main function to orchestrate the creation of resources
def main():
    security_group_id = create_security_group()

    db_url = create_rds_instance(rds_db_instance_id, 'aecon', 'admin', 'a251m2006', region, 'aecon.sql')
    if db_url is None:
        print("Failed to create or retrieve RDS instance. Exiting...")
        return

    ec2_instance_id = create_or_update_ec2_instance(security_group_id, db_url)
    create_s3_bucket('aceon-django-app-adham-zineldin')  # Replace with your desired S3 bucket name
    add_s3_cors_policy('aceon-django-app-adham-zineldin')  # Add CORS policy to the bucket

if __name__ == "__main__":
    main()
