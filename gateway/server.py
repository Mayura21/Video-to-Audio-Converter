import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from bson.objectid import ObjectId


server = Flask(__name__)
# server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"
# server.config["MONGO_URI"] = "mongodb://mongodb:27017/videos"

mongo_video = PyMongo(server, uri="mongodb://mongodb:27017/videos")
mongo_audio = PyMongo(server, uri="mongodb://mongodb:27017/mp3s")

fs_video = gridfs.GridFS(mongo_video.db)
fs_audio = gridfs.GridFS(mongo_audio.db)

try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="rabbitmq", heartbeat=600))
    channel = connection.channel()
except Exception as err:
    print(f"RabbitMQ not available: {err}")
    channel = None

@server.route("/login", methods=["POST"])
def login():
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err
    

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    if err:
        return err
    access = json.loads(access)

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "Exactly 1 files required", 400
        
        for _, f in request.files.items():
            print("Uploading file", flush=True)
            err = util.upload(f, fs_video, channel, access)

            if err:
                print(err, flush=True)
                return err
        return "success!", 200
    else:
        return "Not authorized", 401
    

@server.route("/download", methods=["GET"])
def download():
    access, err = validate.token(request)
    if err:
        return err
    access = json.loads(access)

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required", 400
        
        try:
            out = fs_audio.get(ObjectId(fid_string))
            return send_file(out, download_name=f'{fid_string}.mp3')
        except Exception as e:
            print(e)
            return "internal server error", 500
        
    return "not authorized", 401

if __name__ == "__main__":
    server.run("0.0.0.0", port=8080)