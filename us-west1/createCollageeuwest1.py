import json
import os
import boto3
import math
import io
from PIL import Image

def lambda_handler(event, context):
    EXPRESSION = event['expression']
    s3_arn = event['s3_arn']
    BUCKET_NAME = s3_arn
    
    resource = boto3.resource('s3')
    bucket = resource.Bucket(BUCKET_NAME)
    
    pictures = [p for p in bucket.objects.filter(Prefix=EXPRESSION) if p.key != EXPRESSION]
    
    s3 = boto3.client('s3')
    images = []
    for picture in pictures:
        data = io.BytesIO()
        s3.download_fileobj(BUCKET_NAME, picture.key, data)
        images.append(data)
    
    iteration = 500
    collage = Image.new("RGBA", (iteration*math.ceil(len(images)/2), 2*iteration))
    size = math.ceil(len(images) / 2)
    
    for i in range(size):
        for j in range(2):
            if len(images):
                img = Image.open(images[0])
                img = img.resize((iteration,iteration))
                collage.paste(img, (i*iteration, j*iteration))
                images.pop(0)
            
    buffer = io.BytesIO()
    collage.save(buffer, "PNG")
    buffer.seek(0) 
    
    collage_name = os.path.basename(os.path.normpath(EXPRESSION))
    
    result = s3.put_object(
        Bucket=BUCKET_NAME,
        Key="collages/" + collage_name + ".png",
        Body=buffer,
        ContentType='image/png',
    )
    
    if result['ResponseMetadata']['HTTPStatusCode'] == 200:
        response = "True"
    else:
        response = "False"
    
    return {
        'status': response
    }
