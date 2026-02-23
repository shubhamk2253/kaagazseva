import boto3
from botocore.exceptions import ClientError
from flask import current_app
import uuid

class S3Storage:
    @staticmethod
    def _get_client():
        return boto3.client(
            's3',
            aws_access_key_id=current_app.config['AWS_ACCESS_KEY'],
            aws_secret_access_key=current_app.config['AWS_SECRET_KEY'],
            region_name=current_app.config['AWS_REGION']
        )

    @staticmethod
    def upload_file(file_obj, folder="documents"):
        """Uploads a file and returns the unique S3 Key."""
        s3 = S3Storage._get_client()
        file_extension = file_obj.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{folder}/{uuid.uuid4().hex}.{file_extension}"
        
        try:
            s3.upload_fileobj(
                file_obj,
                current_app.config['AWS_BUCKET_NAME'],
                unique_filename,
                ExtraArgs={'ContentType': file_obj.content_type}
            )
            return unique_filename
        except ClientError as e:
            current_app.logger.error(f"S3 Upload Error: {e}")
            return None

    @staticmethod
    def get_presigned_url(file_key, expires_in=3600):
        """Generates a temporary link for viewing documents securely."""
        s3 = S3Storage._get_client()
        try:
            return s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': current_app.config['AWS_BUCKET_NAME'], 'Key': file_key},
                ExpiresIn=expires_in
            )
        except ClientError:
            return None
