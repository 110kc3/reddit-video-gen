import boto3
from botocore.exceptions import NoCredentialsError
from io import BytesIO
from Secrets.aws_secrets import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import os


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


def __get_existing_post_ids(bucket_name):
    s3 = boto3.client('s3')
    post_ids_without_ext = []

    try:
        s3_objects = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' not in s3_objects:
            return post_ids_without_ext

        for obj in s3_objects['Contents']:
            filename = obj['Key']
            post_id = os.path.splitext(filename)[0]  # Remove the '.txt' extension
            post_ids_without_ext.append(post_id)

    except Exception as e:
        print(f"Error fetching existing post IDs from S3: {e}")

    return post_ids_without_ext
def upload_video_id_to_s3(video_id, bucket_name, video_description, video_tags):
    s3 = boto3.client('s3')
    file_content = f"Video ID: {video_id}\n\nVideo Description:\n{video_description}\n\nVideo Tags:\n{', '.join(video_tags)}"
    file_key = f"{video_id}.txt"

    s3.put_object(Body=file_content, Bucket=bucket_name, Key=file_key)
