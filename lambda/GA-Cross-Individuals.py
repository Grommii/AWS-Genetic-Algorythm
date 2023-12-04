import boto3
import json
import random
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table_genes = dynamodb.Table(os.environ['DDB_TABLE_GENES'])
table_population = dynamodb.Table(os.environ['DDB_TABLE_POPULATION'])

sqs = boto3.client('sqs')
queue_url = os.environ['SQS_FOR_EVALUATION']

def lambda_handler(event, context):
    
    msg_body = json.loads(event['Records'][0]['body'])
    run_id = int(msg_body['run_id'])
    is_crossed = False
    response_genes = table_genes.scan()
    genes = response_genes['Items']

    response_population = table_population.query(
        IndexName = 'run_id-score-index',
        Limit = int(os.environ['GA_POPULATION_SIZE_FOR_CROSSING']),
        ScanIndexForward = False,
        KeyConditionExpression = 'run_id = :run_id',
        ExpressionAttributeValues = {
            ":run_id": run_id
        },
    )
    population = response_population['Items']
    individs = random.sample(population, 2)
    
    crossed_individ = dict()
    crossed_individ['generation'] = 0
    crossed_individ['birthtime'] = datetime.now().strftime("%Y%m%d%H%M%S")
    crossed_individ['run_id'] = run_id
    crossed_individ['birth_action'] = "crossed"
    crossed_individ['parents'] = []
    crossed_individ['id'] = ""
    crossed_individ['genes'] = individs[0]['genes']
    
    for individ in individs:
        print("Chosen individ:", individ['id'])
        crossed_individ['parents'].append(individ['id'])
        if crossed_individ['generation'] < individ['generation']:
            crossed_individ['generation'] = individ['generation']
    crossed_individ['generation'] += 1
    
    
    is_id_equal = lambda gene, id: gene["id"] == id

    for index, gen in enumerate(individs[0]['genes']):
        new_gene = random.choice(individs)['genes'][index]
        crossed_individ['id'] += new_gene['id']
        id_value = new_gene['id']
        matching_genes = filter(lambda gene: is_id_equal(gene, id_value), genes)
        crossed_individ['genes'][index] = next(matching_genes, None)
    
    print("Crossd individ:", crossed_individ['id'])
    
    is_crossed = True
    for individ in individs:
        if individ['id'] == crossed_individ['id']:
            is_crossed = False
    
    if not is_crossed:
        return{
            'statusCode': 200,
            'is_crossed': False
        }
    
    json_individ = json.dumps(crossed_individ, default = str)
    
    sqsresponse = sqs.send_message(
        QueueUrl = queue_url,
        MessageBody = json_individ
    )
    
    msgID = sqsresponse['MessageId']

    # Return a success message
    return {
        'statusCode': 200,
        'MessageId': msgID,
        'body': json_individ,
        'is_crossed': True
    }