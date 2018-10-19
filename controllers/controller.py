import os
import boto3
import requests
import shutil
import uuid
from controllers.s3_client import S3Client
from gtts import gTTS
from pydub import AudioSegment


class Reddit:

    def __init__(self, post_url):
        self.url = "{}.json".format(post_url)
        self.base_mp3 = AudioSegment.empty()
        self.file_code = str(uuid.uuid4())
        self.s3_client = S3Client()
        self.comments = []
        self.batches = set()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux) Gecko/20100101 Firefox/62.0"
        }

    def __save_to_s3(self, ifile):
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("S3_KEY_ID"),
            aws_secret_access_key=os.getenv("S3_KEY")
        )
        out_path = os.path.join(self.file_code, "reddit.mp3")
        s3_client.upload_file(ifile, "redditreader", out_path)

    def __hit_reddit(self):
        resp = requests.get(url=self.url, headers=self.headers)
        return resp.json()

    def __make_voice(self, idx):
        tts = gTTS(text=self.comments[idx], lang='en')
        file_name = "{}_{}.mp3".format(idx, self.file_code)
        file_path = os.path.join(self.file_code, file_name)
        tts.save(file_path)
        self.batches.add(file_name)

    def __concat_files(self, idx):
        batch_file = "{}_{}.mp3".format(idx, self.file_code)
        batch = AudioSegment.from_mp3(os.path.join(os.getcwd(), self.file_code, batch_file))
        self.base_mp3 = self.base_mp3 + batch

    def __extract_metadata(self, resp):
        main = resp[0]["data"]["children"][0]["data"]
        self.title = "Post Title: {}".format(main["title"])
        subreddit = "Subreddit: {}".format(main["subreddit"])
        self.comments.append(subreddit)
        self.comments.append(self.title)

    def harvest_comments(self):
        comments_all = self.__hit_reddit()
        self.__extract_metadata(comments_all)
        posts = comments_all[1]["data"]["children"]
        count = 1
        for i in posts:
            if not i["data"].get("body"):
                continue
            self.comments.append("Comment {}...".format(count))
            self.comments.append(i["data"]["body"])
            count += 1

    def iterate_comments(self):
        for idx, data in enumerate(self.comments):
            self.__make_voice(idx)
            self.__concat_files(idx)
            msg = "Proccessed {}/{}".format(idx + 1, len(self.comments))
            print(msg, end="\r")

    def save_results(self):
        file_name = "reddit.mp3"
        file_path = os.path.join(os.getcwd(), self.file_code, file_name)
        self.base_mp3.export(file_path, format="mp3")
        self.s3_client.save_to_s3(file_path, self.file_code)
        shutil.rmtree(os.path.join(os.getcwd(), self.file_code))

    def clean_up(self):
        base_path = os.getcwd()
        for ifile in self.batches:
                os.remove(os.path.join(base_path, self.file_code, ifile))

    def runner(self):
        os.mkdir(os.path.join(os.getcwd(), self.file_code))
        self.harvest_comments()
        self.iterate_comments()
        self.clean_up()
        self.save_results()
        return self.file_code
