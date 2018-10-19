import boto3
import tempfile
import os


class S3Client:

    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("S3_KEY_ID"),
            aws_secret_access_key=os.getenv("S3_KEY")
        )
        self.resource = boto3.resource(
            's3',
            aws_access_key_id=os.getenv("S3_KEY_ID"),
            aws_secret_access_key=os.getenv("S3_KEY")
        )

    def save_to_s3(self, ifile, file_code):
        out_path = os.path.join(file_code, "reddit.mp3")
        self.client.upload_file(ifile, "redditreader", out_path)

    def pull_from_s3(self, file_code):
        path = os.path.join(file_code, "reddit.mp3")
        bucket = self.resource.Bucket("redditreader")
        ifile = bucket.Object(path)
        tmp = tempfile.NamedTemporaryFile()
        tmp.name = "{}.mp3".format(file_code)
        with open(tmp.name, 'wb') as f:
            ifile.download_fileobj(f)
            return tmp
