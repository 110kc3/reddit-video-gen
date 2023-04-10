import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO
from Secrets.aws_secrets import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY



def upload_file_to_s3(bucket, file_path, object_name):
    try:
        s3.upload_file(file_path, bucket, object_name)
        print(f"File {file_path} uploaded to S3 bucket {bucket} as {object_name}")
    except NoCredentialsError:
        print("AWS credentials not available")


def download_file_from_s3(bucket, object_name, file_path):
    try:
        s3.download_file(bucket, object_name, file_path)
        print(f"File {object_name} downloaded from S3 bucket {bucket} to {file_path}")
    except NoCredentialsError:
        print("AWS credentials not available")


def delete_file_from_s3(bucket, object_name):
    try:
        s3.delete_object(Bucket=bucket, Key=object_name)
        print(f"File {object_name} deleted from S3 bucket {bucket}")
    except NoCredentialsError:
        print("AWS credentials not available")
