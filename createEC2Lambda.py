import boto3
import os
import json 

ec2 = boto3.resource('ec2')

client = boto3.client('sns')
dynamodb = boto3.client('dynamodb')
ec2_client = boto3.client('ec2')

INSTANCE_TYPE = os.environ['INSTANCE_TYPE']
AMI=os.environ['AMI']
SUBNET_ID=os.environ['SUBNET_ID']
SNS_ARN = os.environ['SNS_ARN']
SNS_MESSAGE = os.environ['SNS_MESSAGE']

def lambda_handler(event, context):  
    instance = ec2.create_instances(
        InstanceType=INSTANCE_TYPE,
        ImageId=AMI,
        SubnetId=SUBNET_ID,
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[{   
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name','Value': 'Dry-run'}]
        }]   
    )
    instance_id = instance[0].id
    print("New instance created:", instance_id)
    
    instance_object = ec2.Instance(instance_id)
   
    metadata = instance_object.describe_attribute(Attribute='userData')
    
    item = {
        'instance_id': {'S': instance_id},
        'UserData': {'S': json.dumps(metadata)}
    }
    
    table_name = 'brownBagEc2MetaDataStore'  
    dynamodb.put_item(
        TableName=table_name, 
        Item=item
    )
    
    response = client.publish(
        TopicArn=SNS_ARN,
        Message=SNS_MESSAGE
    )
    
    return {
        'statusCode': 200,
        'body': 'Metadata stored in DynamoDB'
    }
