import json
import boto3
import os
import botocore

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DDB_TABLE_POPULATION'])

def lambda_handler(event, context):
    
    individ = json.loads(event['Records'][0]['body'])
    if isinstance(individ['generation'], str):
        individ['generation'] = int(individ['generation'])
    print(individ)
    
    try:
        table.put_item(
            Item = individ,
            ConditionExpression = 'attribute_not_exists(id)'
            )
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] != 'ConditionalCheckFailedException':
            raise
        print("Insert ignored, because individ already exists.")
    
    return {
        'statusCode': 200
    }