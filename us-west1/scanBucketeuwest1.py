import base64
import json
import boto3
from botocore.exceptions import ClientError
from botocore.vendored import requests
from urllib.parse import urlparse

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    photo_path = event['photo_path']
    s3_arn = event['s3_arn']
    
    url = urlparse(photo_path)
    BUCKET_NAME, KEY = url.path.split('/', 2)[1:]
    
    s3 = boto3.client('s3')
    with open('/tmp/' + 'pic1', 'wb') as f:
        s3.download_fileobj(BUCKET_NAME, KEY, f)


    with open('/tmp/' + 'pic1', 'rb') as f:
        base64_image=base64.b64encode(f.read())
        base_64_binary = base64.decodebytes(base64_image)
        image_bytes = {'Bytes': base_64_binary}
    
    client = boto3.client('rekognition')
    
    response = client.detect_faces(Image=image_bytes, Attributes=['ALL'])

    face_json = {
        "pictureKey": KEY,
        "response": response
    }
    return {
        'list_recognised_faces': str(face_json),
        's3_arn': s3_arn
    }