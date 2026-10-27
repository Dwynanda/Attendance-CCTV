import cv2
from ultralytics import YOLO
import face_recognition
import time
import glob
import os

cctv = "./footage/person_incoming2.mkv" #  <-- IP CCTV
kamera = cv2.VideoCapture(cctv, cv2.CAP_FFMPEG)
face_model = YOLO("./model/yolo11n-face.pt") #  <-- "yolo11n-face.pt" adalah model khusus deteksi wajah
nomor = 0
waktu = 0
waktu_interval = 0.7

training = face_recognition.load_image_file("./training/dw.jpeg")
training_ncode = face_recognition.face_encodings(training)
dtrain = training_ncode[0]

while True:
    ret, frame = kamera.read()
    if not ret or frame is None:
        break

    # grey = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face = face_model.predict(frame, conf=0.25, verbose=False)
    box = face[0].plot()

    for rectangle in face[0].boxes:
        kiri, atas, kanan, bawah = map(int, rectangle.xyxy[0].tolist())
        crop = frame[atas:bawah, kiri:kanan]
        if crop.size == 0:
            continue

        nomor += 1
        cv2.imwrite(f"./faces/{nomor}.jpg", crop)
        waktu = time.time()
        img = face_recognition.load_image_file(f"./faces/{nomor}.jpg")
        encode = face_recognition.face_encodings(img)
    
        if len(encode) > 0:
            compare = face_recognition.compare_faces([dtrain], encode[0])
            if compare[0]:
                print(f"Wajah terdeteksi, dan berhasil di encode, {compare}")
            else:
                print(f"Gagal melakukan proses encode!, {compare}")
        else:
            continue

    face_box = face[0].plot()
    resize_win = cv2.resize(face_box, (900, 600))
    cv2.imshow("CCTV", resize_win)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

kamera.release()
cv2.destroyAllWindows()

# for jpg in glob.glob("./faces/*"):
#     if os.path.isfile(jpg):
#         os.remove(jpg)

print("PROSES SELESAI!")

