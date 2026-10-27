import cv2
from ultralytics import YOLO
import face_recognition
import time
import glob
import os

cctv = "./footage/person_exit.mkv" #  <-- IP CCTV
kamera = cv2.VideoCapture(cctv, cv2.CAP_FFMPEG)
person_model = YOLO("./model/yolo11n.pt") #  <-- "yolo11n-face.pt" adalah model khusus deteksi wajah
nomor = 0
waktu = 0
waktu_interval = 0.7

while True:
    ret, frame = kamera.read()
    if not ret or frame is None:
        break

    # grey = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    person = person_model.predict(frame, classes=[0], imgsz=960, conf=0.5, verbose=False)
    box = person[0].plot()

    for rectangle in person[0].boxes:
        kiri, atas, kanan, bawah = map(int, rectangle.xyxy[0].tolist())
        crop = frame[atas:bawah, kiri:kanan]
        if crop.size == 0:
            continue

        nomor += 1
        cv2.imwrite(f"./person/{nomor}.jpg", crop)
        if len(person) > 0:
            print("Terdeteksi seseorang!")

    person_box = person[0].plot()
    resize_win = cv2.resize(person_box, (900, 600))
    cv2.imshow("CCTV", resize_win)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

kamera.release()
cv2.destroyAllWindows()

# for jpg in glob.glob("./faces/*"):
#     if os.path.isfile(jpg):
#         os.remove(jpg)

print("PROSES SELESAI!")

