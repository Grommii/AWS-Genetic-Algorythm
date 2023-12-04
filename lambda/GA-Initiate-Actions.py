import json
import boto3
import os

sqs = boto3.client('sqs')

def lambda_handler(event, context):
    
    run_id = event['run_id']
    json_request = json.dumps({'run_id':run_id})
    
    for key,value in event.items():
        if key == "get_random":
            
            print("Initiating get_random:", value)
            queue_url = os.environ['SQS_ADD_RANDOM_INDIVIDUAL']
            for i in range(value):
                sqsresponse = sqs.send_message(
                    QueueUrl = queue_url,
                    MessageBody = json_request
                )
            
        elif key == "mutate":
            print("Initiating mutate:", value)
            queue_url = os.environ['SQS_MUTATE_INDIVIDUAL']
            for i in range(value):
                sqsresponse = sqs.send_message(
                    QueueUrl = queue_url,
                    MessageBody = json_request
                )
            
        elif key == "cross":
            print("Initiating cross:", value)
            queue_url = os.environ['SQS_CROSS_INDIVIDUALS']
            for i in range(value):
                sqsresponse = sqs.send_message(
                    QueueUrl = queue_url,
                    MessageBody = json_request
                )
            
        elif key == "run_id":
            print("Run_id gathered:", value)
        else:
            print("Unknown action!")

    
    return {
        'statusCode': 200
    }
