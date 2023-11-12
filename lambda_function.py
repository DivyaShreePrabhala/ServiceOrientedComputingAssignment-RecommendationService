import json
import requests
import boto3

dynamodb = boto3.resource('dynamodb')
recommendations_table = dynamodb.Table('Recommondations')


def lambda_handler(event, context):
    # Assuming you have the recordId in the event, replace it accordingly
    health_records_url = "https://r7jfk2x654.execute-api.eu-north-1.amazonaws.com/health-records/"
    record_id = event.get('pathParameters', {}).get('recordId')

    if not record_id:
        return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Record ID is required'}),
                'headers': {'Content-Type': 'application/json'}
        }
    health_records_url =  health_records_url + "/" + record_id

    # Fetch health record from the provided URL
    health_record_response = requests.get(health_records_url)

    try:
        # Convert the response directly to JSON
        health_record = health_record_response.json()
    except json.JSONDecodeError:
        return {
            'statusCode': health_record_response.status_code,
            'body': json.dumps({'error': 'Failed to decode JSON from health record response.'})
        }

    # Continue processing the health record...
    if health_record_response.status_code == 200:
        # Extract relevant information from the health record
        weight = health_record.get('weight', 0)
        height = health_record.get('height', 0)
        blood_pressure = health_record.get('bloodPressure', 0)

        # Generate health recommendations based on a simple calculation
        recommendations = generate_recommendations(weight, height, blood_pressure)

        # Save recommendations to DynamoDB
        save_recommendations(record_id, recommendations)

        return recommendations
    else:
        return {
            'statusCode': health_record_response.status_code,
            'body': json.dumps({'error': 'Failed to fetch health record'})
        }

def generate_recommendations(weight, height, blood_pressure):
    recommendations = {}

    # Example: Weight-related recommendation
    if weight > 90:
        recommendations['weight'] = 'Consider consulting with a nutritionist to create a personalized weight management plan.'
    elif weight < 50:
        recommendations['weight'] = 'Ensure you are meeting your daily caloric needs for healthy weight gain.'
    else:
        recommendations['weight'] = 'Maintain a balanced diet and exercise regularly for overall well-being.'

    # Example: Height-related recommendation
    if height < 160:
        recommendations['height'] = 'Ensure you are getting proper nutrition to support healthy growth.'
    else:
        recommendations['height'] = 'Maintain a healthy lifestyle to support overall health and well-being.'

    # Example: Blood pressure-related recommendation
    if blood_pressure > 130:
        recommendations['blood_pressure'] = 'Consider monitoring your blood pressure regularly and consult a healthcare professional.'
    else:
        recommendations['blood_pressure'] = 'Maintain a low-sodium diet and engage in regular exercise to support healthy blood pressure.'

    return recommendations


def save_recommendations(record_id, recommendations):
    # Save recommendations to DynamoDB
    try:
        response = recommendations_table.put_item(
            Item={
                'recordId': record_id,
                'recommendations': json.dumps(recommendations)
            }
        )
        print("Recommendations saved successfully:", response)
    except Exception as e:
        print("Error saving recommendations to DynamoDB:", str(e))
