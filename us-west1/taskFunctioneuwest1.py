import json
import boto3

def lambda_handler(event, context):
    s3_arn = event['s3_arn']
    
    BUCKET_NAME = s3_arn
    PICTURES = "pictures/"
    COLLAGES = "collages/"
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(BUCKET_NAME)
    
    pictures = [p for p in bucket.objects.filter(Prefix=PICTURES) if p.key != PICTURES]

    
    s3 = boto3.client('s3')
    
    photos_paths = []
    location = s3.get_bucket_location(Bucket=BUCKET_NAME)['LocationConstraint']
    for picture in pictures:
        url = "https://s3-%s.amazonaws.com/%s/%s" % (location, BUCKET_NAME, picture.key)
        photos_paths.append(url)
    
    return {
        'photos_paths': photos_paths,
        'photos_list_size': len(photos_paths),
        's3_arn': [s3_arn]*len(photos_paths)
    }