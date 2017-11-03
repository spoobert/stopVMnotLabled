import googleapiclient.discovery
from sys import argv
import sendgrid
import os
from sendgrid.helpers.mail import *
import json



def stopInstance( longestName, compute, projId, zone ):
    return compute.instances().stop( project = projId, zone = zone, instance = longestName ).execute()
    
    


def notify( body ):
    sg = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    from_email = Email("toel3my@gmail.com")
    to_email = Email("toel3my@gmail.com")
    subject = "Notification on stop procedure"
    content = Content("text/plain", body )
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    print(response.status_code)
    print(response.body)
    print(response.headers)

def main():    
    
    compute = googleapiclient.discovery.build('compute','v1')
    projId = argv[1]
    warnings = []
    errors = []
    stopped = []
    #gather all restservers
    instances = compute.instances().aggregatedList( project = projId ).execute()

    #check if their are any items in instances: sort running set and stopped set
    for zonepath , result in instances['items'].items():
        if 'instances' in result:
            for instance in result['instances']:
                if instance.get('labels', {} ).get('persistent', 'false') != 'true' and instance['status'] == 'RUNNING':
                    zone = zonepath.split('/')[1]
                    stopRes = stopInstance( instance['name'] , compute , projId , zone )
                    warnings +=  [ (instance['name'] , w ) for w in stopRes.get( 'warnings' , [] )]
                    errors += [ (instance['name'] , e ) for e in stopRes.get( 'error' , {} ).get( 'errors' , [] ) ]
                    if 'error' not in instance:
                        stopped.append(instance['name'])

    if stopped or warnings or errors:
        notify('\nStopped instances:\n{}Warnings:\n{}\nErrors:\n{}\n'.format(*map(json.dumps, [stopped, warnings, errors])))
    
    
if __name__ == "__main__":
    
    main() 
