
import json
from enum import Enum
import os
import boto3

s3 = boto3.client('s3')
resource = boto3.resource('s3')
DICRECTORY_NAME_SAD = "pictures/sadpictures" + "/"
DICRECTORY_NAME_HAPPY = "pictures/happypictures"  + "/"

class Folder_type(Enum):
    HAPPY_FOLDER = 1
    SAD_FOLDER = 2

def upload_image_to_s3(image_obj, imageKey, folder_type, BUCKET_NAME):
    photo_name = os.path.basename(os.path.normpath(imageKey))
    
    if folder_type == Folder_type.HAPPY_FOLDER:
        KEY = DICRECTORY_NAME_HAPPY + photo_name
    else:
        KEY = DICRECTORY_NAME_SAD + photo_name
    
    with open('/tmp/' + 'pic1', 'wb') as f:
        s3.download_fileobj(BUCKET_NAME, imageKey, f)
    
    with open('/tmp/' + 'pic1', 'rb') as fd:
        result = s3.put_object(
            Bucket=BUCKET_NAME,
            Key=KEY,
            Body=fd
        )
    
def lambda_handler(event, context):
    retrievedData = event['list_of_list_recognised_faces']
    s3_arn = event['s3_arn'][0]
    BUCKET_NAME = s3_arn

    recognised_overall_faces = []
    recognised_happyfaces_expression = []
    recognised_sadfaces_expression = []
    
    bucket = resource.Bucket(BUCKET_NAME)
    
    s3.put_object(Bucket=BUCKET_NAME, Key = (DICRECTORY_NAME_SAD))
    s3.put_object(Bucket=BUCKET_NAME, Key = (DICRECTORY_NAME_HAPPY))
    
    for data in retrievedData:
        json = eval(data)  #convert str to dict for parsing
        json_response_data = json['response']
        json_pictureKey_data = json['pictureKey']
        
        for img_faces in json_response_data['FaceDetails']:
            face_recognised = img_faces['BoundingBox']
            face_emotions = img_faces['Emotions']
            happy_confidence_final_value = 0.0
            sad_confidence_final_value = 0.0
            for emotion in face_emotions:
                if emotion["Type"] == "HAPPY":
                    happy_confidence_final_value += emotion["Confidence"]
                if emotion["Type"] == "SAD":
                    sad_confidence_final_value += emotion["Confidence"]
            if sad_confidence_final_value < happy_confidence_final_value:
                image_obj = bucket.Object(json_pictureKey_data)
                upload_image_to_s3(image_obj, json_pictureKey_data, Folder_type.HAPPY_FOLDER, BUCKET_NAME)
            else: 
                image_obj = bucket.Object(json_pictureKey_data)
                upload_image_to_s3(image_obj, json_pictureKey_data, Folder_type.SAD_FOLDER, BUCKET_NAME)
    
    list_of_s3_buckets = [DICRECTORY_NAME_SAD, DICRECTORY_NAME_HAPPY]
    return {
        'list_of_list_recognised_faces_byexpression' : list_of_s3_buckets,
        'number_expressions': len(list_of_s3_buckets),
        's3_arn': [s3_arn]*len(list_of_s3_buckets)
    }