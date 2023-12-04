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
    mutate_rate = int(os.environ['GA_MUTATE_RATE_PERCENT'])
    is_mutated = False
    response_genes = table_genes.scan()
    genes = response_genes['Items']

    response_population = table_population.query(
        IndexName = 'run_id-score-index',
        Limit = int(os.environ['GA_POPULATION_SIZE_FOR_MUTATE']),
        ScanIndexForward = False,
        KeyConditionExpression = 'run_id = :run_id',
        ExpressionAttributeValues = {
            ":run_id": run_id
        },
    )
    population = response_population['Items']

    individ = random.choice(population)
    print("Chosen individ: ", individ['id'])

    mutated_individ = dict()
    mutated_individ['generation'] = individ['generation'] + 1
    mutated_individ['birthtime'] = datetime.now().strftime("%Y%m%d%H%M%S")
    mutated_individ['run_id'] = run_id
    mutated_individ['birth_action'] = "mutated"
    mutated_individ['parents'] = [{'id':individ['id']}]
    mutated_individ['id'] = ""
    mutated_individ['genes'] = individ['genes']
    
    is_id_equal = lambda gene, id: gene["id"] == id

    for index, gen in enumerate(individ['genes']):
        
        if random.choice(range(100)) < mutate_rate:
            new_gene = random.choice(genes)
            if individ['genes'][index]['id'] != new_gene['id']:
                is_mutated = True
            mutated_individ['genes'][index] = new_gene
            mutated_individ['id'] += new_gene['id']
        else:
            id_value = individ['genes'][index]['id']
            matching_genes = filter(lambda gene: is_id_equal(gene, id_value), genes)
            mutated_individ['genes'][index] = next(matching_genes, None)
            mutated_individ['id'] += id_value
    
    print("Mutatd individ: ", mutated_individ['id'])
    
    if not is_mutated:
        return{
            'statusCode': 200,
            'is_mutated': False
        }
    
    json_individ = json.dumps(mutated_individ, default = str)
    
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
        'is_mutated': True
    }