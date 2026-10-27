import cv2
from ultralytics import YOLO
import os
import time
from datetime import datetime

cctv = "rtsp://admin:L2034E56@192.168.1.13:554/cam/realmonitor?channel=1&subtype=0" #  <-- IP CCTV
kamera = cv2.VideoCapture(cctv, cv2.CAP_FFMPEG)
folder = "burh"

fps = kamera.get(cv2.CAP_PROP_FPS)
width = int(kamera.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(kamera.get(cv2.CAP_PROP_FRAME_HEIGHT))

if fps <= 0:
    fps = 5

codec = cv2.VideoWriter_fourcc(*'MJPG')
waktu = time.time()
recorder = None
durasi = 20

while True:
    ret, frame = kamera.read()
    if recorder is None or time.time() - waktu >= durasi:
        if recorder is not None:
            recorder.release

        filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        recorder = cv2.VideoWriter(os.path.join(folder, f"{filename}.mkv"), codec, fps, (width, height)) # <-- nama file "test.mkv" nnti diubah jadi format date!
        print(f"{filename}.mkv berhasil disimpan!")
        waktu = time.time()

    recorder.write(frame)
    
    #====window====#
    resize_win = cv2.resize(frame, (800, 600))
    cv2.imshow("CCTV", resize_win)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    #==============#