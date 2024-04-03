import boto3
import traceback

class S3Connector():
    def __init__(self, access_key, secret) -> None:
        self.client = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret
        )
    
    def get_object(self, path):
        try:
            response = self.client.get_object(
                Bucket='auwrn',
                Key=path
            )
            data = response['Body'].read().decode('utf-8')
        except Exception as e:
            print(traceback.format_exc())
            return False
        return data

    def upload_object(self, path, data):
        try:
            self.client.put_object(
                Body=data,
                Bucket='auwrn',
                Key=path
            )
        except Exception as e:
            print(traceback.format_exc())
    
    def get_list(self, prefix):
        res = self.client.list_objects_v2(
            Bucket = 'auwrn',
            Prefix = prefix,
        )
        return res

    def update_config(self, team_id, user_id, data):
        config = self.get_object(f"{team_id}/{user_id}/config.json")
        for key, val in data.items():
            config[key] = val
        self.upload_object(f"{team_id}/{user_id}/config.json", config)
    
    def upload_file_object(self, path, data):
        try:
            self.client.upload_fileobj(
                Fileobj=data,
                Bucket='auwrn',
                Key=path
            )
        except Exception as e:
            print(traceback.format_exc())