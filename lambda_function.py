import json
import boto3
import base64
import requests

def lambda_handler(event, context):

    comment = event['detail']['ticket_event']['comment']['body']
    user_id = event['detail']['ticket_event']['ticket']['requester_id']
    ticket_id = event['detail']['ticket_event']['ticket']['id']
    ticket = event['detail']['ticket_event']['ticket']
    
    comprehend_client = boto3.client('comprehend', region_name='us-west-2')
    
    response = comprehend_client.detect_sentiment(
    Text=comment,
    LanguageCode='en')

    
    if response['Sentiment'] == 'NEGATIVE':
        #publish to sns topic to notify by email
        sns_client = boto3.client('sns')
        sns_response = sns_client.publish(
        TopicArn='arn:aws:sns:us-west-1:805580953652:NegativeZenDeskTicket',
        Message=comment + ' from user ' + str(user_id),
        Subject='Negative Ticket Alert')
            
        # hit zendesk api to update that ticket with priority support tag
        
        base_zendesk_api_url = 'https://z3n-developer.zendesk.com/api/v2/tickets/{}.json'.format(ticket_id)
        auth = 'nickik@amazon.com/token:DIkn8fdSGHLQTcp6AIlvW4fZfM5Yr8tdbu6mMERy'
        base_64_encoded_auth = base64.b64encode(auth.encode('utf-8'))
        #update ticket
        #print(ticket)
        json_ticket = {}
        json_ticket['ticket'] = {}
        json_ticket['ticket']['priority'] = 'urgent'
        json_ticket['ticket']['tags'] = ['Priority Support'] 
    
        ticket_string = json.dumps(json_ticket)
        #print(ticket_string)
        headers = {'Content-Type': 'application/json', 'Authorization': 'Basic ' + base_64_encoded_auth.decode('utf-8')}
        zendesk_response = requests.put(base_zendesk_api_url, headers=headers, data=ticket_string)
        print(zendesk_response.json())
        
    else :
        print('sentiment is positive, do nothing yay!')
    
