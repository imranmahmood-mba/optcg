import logging
import boto3
from botocore.exceptions import ClientError
import os
import logging
import logging.config

logging.config.fileConfig(fname='/Users/imranmahmood/OnePieceDE/util/logging_to_file.conf')
logger = logging.getLogger(__name__)

def upload_file(file_name, bucket, object_name=None):
    """
    Uploads a file to an S3 bucket.

    Parameters:
        file_name (str): The name of the file to be uploaded.
        bucket (str): The name of the S3 bucket where the file will be uploaded.
        object_name (str, optional): The name of the object in the S3 bucket. If not specified, the base name of the file will be used.

    Returns:
        None

    Raises:
        ClientError: If there is an error while uploading the file to the S3 bucket.

    Logs:
        Logs an error message if there is an error while uploading the file to the S3 bucket.
        Logs an info message if the file is successfully uploaded to the S3 bucket.
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(f"Error in the method upload_file: {e}")
        raise e
    else:
        logging.info(f"{object_name} successfully uploaded to s3 bucket: {bucket}")
