import pika, json, tempfile, os
from bson.objectid import ObjectId
# import moviepy
from moviepy.video.io.VideoFileClip import VideoFileClip


def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)

    # Empty temp file
    tf = tempfile.NamedTemporaryFile()

    # video contents
    out = fs_videos.get(ObjectId(message["video_fid"]))

    # Add video content to empty file
    tf.write(out.read())

    # Create audio from temp video files
    # audio = moviepy.editor.VideoFileClip(tf.name).audio
    # audio = moviepy.video.io.VideoFileClip.VideoFileClip(tf.name).audio
    audio = VideoFileClip(tf.name).audio
    tf.close()

    # Write audio to the file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3"
    audio.write_audiofile(tf_path)

    # Save the file to mongo
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()

    os.remove(tf_path)

    message["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "failed to pusblish message"