#!/usr/bin/env python
import collections
import tempfile
import time

import cv2
from flask import Flask, Response, request

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

DIM = 640, 480
last_time = 0
cam = None
for cam_i in (3, 4, 5):
    cam = cv2.VideoCapture(cam_i)
    if cam.isOpened():
        break
if not cam.isOpened():
    cam.release()
    cv2.destroyAllWindows()
    raise IOError("Cannot open webcam")

# RESOLUTION
# cam.set(3, DIM[0])
# cam.set(4, DIM[1])
for i in range(999):
    print(i, cam.get(i))
# cam.set(cv2.CAP_PROP_BRIGHTNESS, 15)

fps_to_show = collections.deque([0] * 20)


def get_frame():
    try:
        ret, frame = cam.read()
    except cv2.error:
        pass
    else:
        if ret:
            return cv2.imencode('.png', frame)[1].tostring()
            # cv2.imwrite('temp.jpg', frame)
            # return open('temp.jpg', 'rb').read()


done = False


@app.route('/')
def index():
    return 'ola k ase'


@app.route('/stop')
def stop():
    global done
    done = True
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return 'stoped'


def gen():
    global cam
    global last_time
    while not done:
        now = time.time()
        t = now - last_time
        last_time = now
        fps_to_show.popleft()
        fps_to_show.append(1 / t)
        fps_text = round(sum(fps_to_show) / len(fps_to_show), 1)
        print(fps_text)
        frame = get_frame()
        if frame is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
                   )

    del cam


@app.route('/video_feed')
def video_feed():
    resp = Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    print('RESP', resp)
    return resp


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
