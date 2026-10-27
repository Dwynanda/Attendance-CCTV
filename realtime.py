import cv2
from ultralytics import YOLO
import face_recognition
import time
import glob
import os
import mysql.connector
import pickle
from datetime import datetime

cctv = "./footage/person_incoming1.mkv" #  <-- IP CCTV
kamera = cv2.VideoCapture(cctv, cv2.CAP_FFMPEG)
face_model = YOLO("./model/yolo11n-face.pt") #  <-- "yolo11n-face.pt" adalah model khusus deteksi wajah
person_model = YOLO("./model/yolo11n.pt") # <-- model yang difungsikan untuk deteksi objek/manusia

nomor = 0
waktu = 0
waktu_interval = 0.5

encoded = []
personnamed = []
present = set()
foreign_key = []


#==============DATABASE======================
database = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "",
    database = "attendance_cctv"
)
cursors = database.cursor()

command = """
    SELECT id, name, encoded
    FROM encoding_data
"""

cursors.execute(command)
data = cursors.fetchall()

for id, name, ncode in data:
    ubah = pickle.loads(ncode)
    encoded.append(ubah)
    personnamed.append(name)
    foreign_key.append(id)

command2 = """
        INSERT INTO absensi (person, img, waktu) VALUES (%s, %s, %s)
"""
#==============================================

def data_add(person_name, frame):
    if person_name != "Unknown" and person_name not in present:
        success, buffer = cv2.imencode(".jpg", frame)
        datetime_database = datetime.now()

        if success:
            person_img = buffer.tobytes()

            index = personnamed.index(person_name)
            id_karyawan = foreign_key[index]

            cursors.execute(
                command2,
                (id_karyawan, person_img, datetime_database)
            )

            database.commit()
            present.add(person_name)


while True:
    ret, frame = kamera.read()
    if not ret or frame is None:
        break

    face = face_model.predict(frame, conf=0.25, verbose=False)
    for rectangle in face[0].boxes:
        kiri, atas, kanan, bawah = map(int, rectangle.xyxy[0].tolist())
        crop_face = frame[atas:bawah, kiri:kanan]
        if crop_face.size == 0:
            continue

        nomor += 1
        cv2.imwrite(f"./faces/{nomor}.jpg", crop_face)

        if time.time() - waktu >= waktu_interval:
            waktu = time.time()
            img = face_recognition.load_image_file(f"./faces/{nomor}.jpg")
            encode = face_recognition.face_encodings(img)
        
            if len(encode) > 0:
                jarak = face_recognition.face_distance(encoded, encode[0])

                if len(jarak) > 0:
                    guessing_name = jarak.argmin()

                    if jarak[guessing_name] < 0.5:
                        person_name = personnamed[guessing_name]
                        print(f"Wajah dikenali: {person_name}, jarak: {jarak[guessing_name]:.3f}")
                        data_add(person_name, frame)
                       
                    else:
                        person_name = "Unknown"
                        data_add(person_name, frame)
                        print(f"Wajah tidak dikenal, jarak terkecil: {jarak[guessing_name]:.3f}")
            else:
                continue

    face_box = face[0].plot()
    resize_win = cv2.resize(face_box, (900, 600))
    cv2.imshow("CCTV", resize_win)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

kamera.release()
cv2.destroyAllWindows()

for jpg in glob.glob("./faces/*"):
    if os.path.isfile(jpg):
        os.remove(jpg)

print("PROSES SELESAI!")

