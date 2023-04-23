import boto3

class S3Connector():
    def __init__(self) -> None:
        self.client = boto3.client(
            's3',
            aws_access_key_id='your_access_key',
            aws_secret_access_key='your_secret_key'
        )
    
    def get_object(self, path):
        response = self.client.get_object(
            Bucket='auwrn',
            Key=path
        )
        data = response['Body'].read()
        return data

    def upload_object(self, path, data):
        self.client.s3.put_object(
            Body=data,
            Bucket='auwrn',
            Key=path
        )
