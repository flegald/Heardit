import os
import json
from controllers.controller import Reddit
from controllers.s3_client import S3Client
from flask import Flask, render_template, send_from_directory, send_file, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/api/submit", methods=['POST'])
def process_post():
    post_url = request.values["submission"]
    file_code = Reddit(post_url).runner()
    return json.dumps({"code": file_code})


@app.route("/api/download/<file_code>")
def download(file_code):
    tmp_file = S3Client().pull_from_s3(file_code)
    print(tmp_file.name)
    return send_file(tmp_file.name, attachment_filename=tmp_file.name, mimetype="audio/mpeg", as_attachment=True)
