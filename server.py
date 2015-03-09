from flask import Flask, request, jsonify
from moviepy.editor import *
from src.s3_manager import S3Manager
from src.config_parser import get_config
from src.video_manager import VideoManager
import urllib2
import os,binascii
import json
import requests

app = Flask(__name__)
app.debug = True

@app.route("/convert", methods=["POST"])
def convert():
    s3Manager = S3Manager(get_config())

    if not request.data:
        return 'Error', 406

    json_request = json.loads(request.data);
    if 'url' not in json_request:
        return 'url property is not present in the payload', 406

    url = json.loads(request.data)['url']

    gif_filepath = saving_to_local(url)

    result = VideoManager().convert(gif_filepath)

    s3_path_to_mp4 = s3Manager.upload(result.mp4, "./tmp/%s" % result.mp4)
    s3_path_to_png = s3Manager.upload(result.snapshot, "./tmp/%s" % result.snapshot)

    if 'webhook' in json_request:
        webhook = json.loads(request.data)['webhook']

        payload = {'mp4': s3_path_to_mp4, 'snapshot': s3_path_to_png}
        requests.post(webhook, data=payload)

    return jsonify(mp4=s3_path_to_mp4, snapshot=s3_path_to_png)


def saving_to_local(url):

    response = urllib2.urlopen(url)
    contents = response.read()

    random_filename = binascii.b2a_hex(os.urandom(15))

    gif_filepath = "./tmp/%s.gif" % (random_filename)
    f = open(gif_filepath, 'wb')
    f.write(contents)
    f.close()

    return gif_filepath


if __name__ == "__main__":
    app.run()
