import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client(
    "s3",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

BUCKET = os.getenv("AWS_BUCKET_NAME")

def upload_file(file, key_name):

    s3.upload_fileobj(
        file,
        BUCKET,
        key_name,
        ExtraArgs={
            "ContentType": file.content_type
        }
    )

    return key_name


def generate_signed_url(key_name, expiration=300):

    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET,
                "Key": key_name
            },
            ExpiresIn=expiration
        )
        return url
    except ClientError:
        return None
