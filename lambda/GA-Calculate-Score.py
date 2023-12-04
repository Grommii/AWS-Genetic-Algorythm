import json
import boto3
import os

sqs = boto3.client('sqs')
queue_url = os.environ['SQS_ADD_TO_POPULATION']

def lambda_handler(event, context):

    individ = json.loads(event['Records'][0]['body'])
    print(individ)
    
    individ_id = ""
    score = 0
    individ_for_insert = dict()
    individ_for_insert['genes'] = []

    genes = individ['genes']
    for gen in genes:
        individ_id += gen['id'] #+ "#"
        individ_for_insert['genes'].append({'id':gen['id']})
        score += int(gen['properties']['value'])
    
    print("individ_id: ", individ_id)
    print("score: ", score)
    
    individ_for_insert['generation'] = individ['generation']
    individ_for_insert['birthtime'] = individ['birthtime']
    individ_for_insert['id'] = individ_id
    individ_for_insert['score'] = score
    individ_for_insert['birth_action'] = individ['birth_action']
    if 'run_id' in individ:
        individ_for_insert['run_id'] = individ['run_id']
    else:
        individ_for_insert['run_id'] = 1
    if 'parents' in individ:
        individ_for_insert['parents'] = individ['parents']
    
    json_individ = json.dumps(individ_for_insert, default = str)
    
    sqsresponse = sqs.send_message(
        QueueUrl = queue_url,
        MessageBody = json_individ
    )
    
    msgID = sqsresponse['MessageId']
    
    return {
        'statusCode': 200,
        'MessageId': msgID,
        'body': json_individ
    }
