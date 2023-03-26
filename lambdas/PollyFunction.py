import base64
from io import BytesIO
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

pollyClient = boto3.client('polly')
s3Client = boto3.client('s3')

def handler(event, context):
    logger.info(event)

    split = event['requestContext']['http']['path'].split('/')
    response = None

    if len(split) == 2:
        text = split[1]
        if len(text) < 10:
            pollyResponse = pollyClient.synthesize_speech(
                Engine='standard',
                LanguageCode='ko-KR',
                OutputFormat='mp3',
                Text=text,
                VoiceId='Seoyeon'
            )

            logger.info(pollyResponse)

            bytes = pollyResponse['AudioStream'].read()

            s3Client.upload_fileobj(
                BytesIO(bytes),
                'polly-bucket-us-west-2-434623153115',
                text,
                ExtraArgs={
                    'ContentType': 'audio/mpeg'
                }
            )

            response = {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'audio/mpeg'
                },
                'body': base64.b64encode(bytes).decode('utf-8'),
                'isBase64Encoded': True
            }

    if response:
        return response
    else:
        return {
            'statusCode': 400
        }
