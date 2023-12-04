import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DDB_TABLE_GENES'])

def lambda_handler(event, context):
    
    with table.batch_writer() as batch:
        
        # Loop through the range of 0 to 9
        for i in range(10):
            # Create a record with id and properties fields
            record = {
                'id': str(i), # Convert i to string
                'properties': {
                    'value': i # Use i as the value
                }
            }
            # Insert the record into the table
            batch.put_item(Item=record)
    
    # Return a success message
    return {
        'statusCode': 200,
        'body': 'Inserted 10 records into genes table'
    }