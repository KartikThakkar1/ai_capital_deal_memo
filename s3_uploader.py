# this code uploads all the files in the data/ to an S3 bucket on cloud.

import boto3
from botocore.exceptions import NoCredentialsError
import os
from config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME

def upload_to_s3(file_path, base_folder:"data", s3_filename=None):
    """
    Uploads a file to S3 only if it doesn't already exist.
    """
    s3 = boto3.client('s3',
                      region_name=AWS_REGION,
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    if not s3_filename:
        # this will get relative path like Apple_Deal/k10.pdf
        s3_filename = os.path.relpath(file_path, base_folder).replace("\\", "/")

    # check if file already exists in bucket
    try:
        s3.head_object(Bucket=S3_BUCKET_NAME, Key=s3_filename)
        print(f"Skipping upload, file already exists in S3: {s3_filename}")
        return f"s3://{S3_BUCKET_NAME}/{s3_filename}"
    except s3.exceptions.ClientError as e:
        if e.response['Error']['Code'] != "404":
            raise
    # upload the file if it does not exists already
    try:
        s3.upload_file(file_path, S3_BUCKET_NAME, s3_filename)
        print(f"Uploaded: {file_path} -> s3://{S3_BUCKET_NAME}/{s3_filename}")
        return f"s3://{S3_BUCKET_NAME}/{s3_filename}"
    except Exception as e:
        print("Upload failed:", e)




def upload_all_pdfs_from_folder(folder_path):
    """
    Uploads all PDF files from a folder to S3.
    """
    for filename in os.listdir(folder_path):
        for root, _, files in os.walk(folder_path):
            for filename in files:
                if filename.endswith(".pdf"):
                    file_path = os.path.join(root, filename)
                    upload_to_s3(file_path, base_folder=folder_path)




if __name__ == "__main__":
    folder_path = "data/"
    upload_all_pdfs_from_folder(folder_path)

