import boto3
import json
import random
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DDB_TABLE_GENES'])

sqs = boto3.client('sqs')
queue_url = os.environ['SQS_FOR_EVALUATION']

def lambda_handler(event, context):
    
    response = table.scan()
    genes = response['Items']
    msg_body = json.loads(event['Records'][0]['body'])

    # Create new list with random elements from genes. Elements can repeat in new list.
    new_genes = random.choices(genes, k = int(os.environ['GA_INDIVIDUAL_GENES']))
    
    individ = dict()
    individ['generation'] = 0
    individ['birthtime'] = datetime.now().strftime("%Y%m%d%H%M%S")
    individ['run_id'] = msg_body['run_id']
    individ['birth_action'] = "generated"
    individ['genes'] = new_genes
    
    individ_id = ""
    for gen in individ['genes']:
        individ_id += gen['id']
    print("Generated individ:", individ_id)
    
    json_individ = json.dumps(individ, default = str)
    
    sqsresponse = sqs.send_message(
        QueueUrl = queue_url,
        MessageBody = json_individ
    )
    
    msgID = sqsresponse['MessageId']

    # Return a success message
    return {
        'statusCode': 200,
        'MessageId': msgID,
        'body': json_individ
    }