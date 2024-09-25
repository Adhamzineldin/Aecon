import boto3
import time
from botocore.exceptions import ClientError

region = 'eu-north-1'
# Initialize boto3 clients
ec2_client = boto3.client('ec2', region_name=region)
s3_client = boto3.client('s3', region_name=region)
rds_client = boto3.client('rds', region_name=region)
ec2_resource = boto3.resource('ec2', region_name=region)

# Name of the EC2 instance
instance_name = 'Aceon4'  # Update with your desired instance name
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
            user_data_script = f'''#!/bin/bash
                                    # Update package index
                                    sudo apt update

                                    # Install Python 3.12 and necessary packages
                                    sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip libpq-dev postgresql postgresql-contrib nginx curl git

                                    # Create a directory for the Django app
                                    sudo mkdir -p /home/ubuntu/mydjangoapp

                                    # Clone your Django app from your repository
                                    git clone https://github.com/Adhamzineldin/Aecon.git /home/ubuntu/mydjangoapp  # Update this URL

                                    # Navigate to the application directory
                                    cd /home/ubuntu/mydjangoapp

                                    # Create a virtual environment using Python 3.12
                                    /usr/bin/python3.12 -m venv venv

                                    # Activate the virtual environment
                                    source venv/bin/activate

                                    # Upgrade pip to the latest version
                                    pip install --upgrade pip

                                    # Install dependencies from requirements.txt
                                    pip install -r requirements.txt

                                    # Create .env file with database URL
                                    echo "DATABASE_URL={db_url}" > .env

                                    # Set environment variables for Django
                                    echo 'export DJANGO_SETTINGS_MODULE=mydjangoapp.settings' | tee -a ~/.bashrc
                                    echo 'export PYTHONPATH=/home/ubuntu/mydjangoapp' | tee -a ~/.bashrc
                                    echo 'SECRET_KEY=h6#9_tw1#cc_q7*da(1=ni(-%t45wx)qvlyx+c6wt7+5)aqk0r' | tee -a ~/.bashrc
                                    echo 'API_KEY=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' | tee -a ~/.bashrc
                                    echo 'DEBUG=True' | tee -a ~/.bashrc
                                    echo 'WEBSITE_HOSTNAME=127.0.0.1' | tee -a ~/.bashrc

                                    # Migrate database
                                    /usr/bin/python3.12 manage.py migrate

                                    # Collect static files
                                    /usr/bin/python3.12 manage.py collectstatic --noinput

                                    # Start Gunicorn to serve the Django app
                                    gunicorn mydjangoapp.wsgi:application --bind 0.0.0.0:8000 --daemon

                                    # Set up Nginx to reverse proxy to Gunicorn
                                    sudo bash -c 'cat > /etc/nginx/sites-available/mydjangoapp <<EOF
                                    server {{
                                        listen 80;
                                        server_name _;  # Change to your server's domain name or public IP

                                        location = /favicon.ico {{ access_log off; log_not_found off; }}
                                        location /static/ {{
                                            root /home/ubuntu/mydjangoapp;
                                        }}

                                        location / {{
                                            include proxy_params;
                                            proxy_pass http://127.0.0.1:8000;
                                        }}
                                    }}
                                    EOF'

                                    # Enable the new Nginx site and remove the default
                                    sudo ln -s /etc/nginx/sites-available/mydjangoapp /etc/nginx/sites-enabled
                                    sudo rm /etc/nginx/sites-enabled/default

                                    # Test Nginx configuration
                                    sudo nginx -t

                                    # Restart Nginx to apply changes
                                    sudo systemctl restart nginx

                                    # Optional: Set the Gunicorn service to start on boot
                                    sudo bash -c 'cat > /etc/systemd/system/gunicorn.service <<EOF
                                    [Unit]
                                    Description=gunicorn daemon
                                    After=network.target

                                    [Service]
                                    User=ubuntu  # Replace with your EC2 username
                                    Group=www-data
                                    WorkingDirectory=/home/ubuntu/mydjangoapp
                                    ExecStart=/home/ubuntu/mydjangoapp/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/mydjangoapp/mydjangoapp.sock mydjangoapp.wsgi:application

                                    [Install]
                                    WantedBy=multi-user.target
                                    EOF'

                                    # Start and enable the Gunicorn service
                                    sudo systemctl start gunicorn
                                    sudo systemctl enable gunicorn

                                    echo "Django application setup complete!"
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
def create_rds_instance(db_instance_id, db_name, username, password):
    try:
        # Check if the RDS instance already exists
        rds_instances = rds_client.describe_db_instances(DBInstanceIdentifier=db_instance_id)
        if rds_instances['DBInstances']:
            print(f"RDS instance {db_instance_id} already exists. Retrieving connection details...")
            return f"postgres://{username}:{password}@{db_instance_id}.{region}.rds.amazonaws.com:5432/{db_name}"
    except ClientError as e:
        if e.response['Error']['Code'] != 'DBInstanceNotFound':
            print(f"Error checking for RDS instance: {e}")
            return None

    try:
        print(f"Creating RDS instance: {db_instance_id}...")
        rds_client.create_db_instance(
            DBInstanceIdentifier=db_instance_id,
            AllocatedStorage=20,
            DBInstanceClass='db.t3.micro',  # Changed to a more widely available instance type
            Engine='postgres',
            MasterUsername=username,
            MasterUserPassword=password,
            DBName=db_name,
            BackupRetentionPeriod=7,  # Keep backups for 7 days
            MultiAZ=False,  # Single AZ deployment for free tier
            PubliclyAccessible=True
        )
        print(f"RDS instance {db_instance_id} is being created.")
        return f"postgres://{username}:{password}@{db_instance_id}.{region}.rds.amazonaws.com:5432/{db_name}"
    except Exception as e:
        print(f"Error creating RDS instance: {e}")
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

    db_url = create_rds_instance(rds_db_instance_id, 'mydatabase', 'myusername', 'mypassword')
    if db_url is None:
        print("Failed to create or retrieve RDS instance. Exiting...")
        return

    ec2_instance_id = create_or_update_ec2_instance(security_group_id, db_url)
    create_s3_bucket('aceon-django-app-adham-zineldin')  # Replace with your desired S3 bucket name
    add_s3_cors_policy('aceon-django-app-adham-zineldin')  # Add CORS policy to the bucket

if __name__ == "__main__":
    main()
