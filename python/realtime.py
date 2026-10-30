import cv2
from ultralytics import YOLO
import face_recognition
import time
import glob
import os
import mysql.connector
import pickle
from datetime import datetime
from flask import Flask, Response
import threading

cctv = "rtsp://admin:L2034E56@192.168.1.13:554/cam/realmonitor?channel=1&subtype=0" #  <-- IP CCTV
kamera = cv2.VideoCapture(cctv, cv2.CAP_FFMPEG)
face_model = YOLO("./python/yolo11n-face.pt") #  <-- "yolo11n-face.pt" adalah model khusus deteksi wajah
# person_model = YOLO("./model/yolo11n.pt") # <-- model yang difungsikan untuk deteksi objek/manusia

app = Flask(__name__)

nomor = 0
waktu = 0
waktu_interval = 1

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

output_frame = None

def generate():
    global output_frame

    while True:
        if output_frame is None:
            continue

        success, buffer = cv2.imencode(".jpg", output_frame)
        if not success:
            continue

        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video')
def video():
    return Response(
        generate(), mimetype='multipart/x-mixed-replace; boundary=frame'
    )

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
            # present.add(person_name)

def process_cctv():
    global output_frame, nomor, waktu

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
            cv2.imwrite(f"./python/faces/{nomor}.jpg", crop_face)

            if time.time() - waktu >= waktu_interval:
                waktu = time.time()
                img = face_recognition.load_image_file(f"./python/faces/{nomor}.jpg")
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
        output_frame = resize_win

    kamera.release()
    for jpg in glob.glob("./python/faces/*"):
        if os.path.isfile(jpg):
            os.remove(jpg)

    cv2.destroyAllWindows()

if __name__ == "__main__":
    threading.Thread(target=process_cctv, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, threaded=True)

print("PROSES SELESAI!")

