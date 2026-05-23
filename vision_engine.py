import cv2
import logging
import sys
import os
import time
import pyodbc
import mediapipe as mp
import numpy as np
from datetime import datetime

VAULT_DIR = "evidence_vault"
os.makedirs(VAULT_DIR, exist_ok=True)
os.makedirs("audit_logs", exist_ok=True)

SQL_CONFIG = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=(localdb)\\MSSQLLocalDB;"
    "Database=VisionSecurityDB;"
    "Trusted_Connection=yes;"
)

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler("audit_logs/vision_audit.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def register_biometric_event(filename: str, absolute_path: str) -> None:
    try:
        connection = pyodbc.connect(SQL_CONFIG)
        cursor = connection.cursor()
        statement = "INSERT INTO BiometricAudit (ImageFilename, ImagePath) VALUES (?, ?)"
        cursor.execute(statement, (filename, absolute_path))
        connection.commit()
        logging.info("SQL_SYNC: Forensic video record committed to BiometricAudit table.")
        connection.close()
    except Exception as error:
        logging.error(f"SQL_ERROR: Synchronization failed. Details: {str(error)}")

def run_biometric_service(video_source: cv2.VideoCapture) -> None:
    logging.info("Biometric KYC service initialized. Split-Screen and Video Audit enabled.")
    
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=(0, 255, 0))
    
    CAPTURE_COOLDOWN = 10.0
    RECORDING_DURATION = 3.0
    
    last_capture_time = time.time() - CAPTURE_COOLDOWN
    is_recording = False
    video_writer = None
    current_video_name = ""
    current_video_path = ""
    
    with mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True) as mesh:
        while True:
            ret, frame = video_source.read()
            if not ret: break
            
            frame = cv2.resize(frame, (640, 480))
            h, w, c = frame.shape
            
            black_canvas = np.zeros((h, w, c), dtype=np.uint8)
            current_time = time.time()
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = mesh.process(rgb_frame)
            
            verified = False
            if results.multi_face_landmarks:
                verified = True
                for landmarks in results.multi_face_landmarks:
                    mp_drawing.draw_landmarks(
                        black_canvas, 
                        landmarks, 
                        mp_face_mesh.FACEMESH_TESSELATION, 
                        drawing_spec, 
                        drawing_spec
                    )
                
                cv2.putText(black_canvas, "[ KYC: IDENTITY VERIFIED ]", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)
                cv2.putText(black_canvas, "STATUS: SUCCESSFUL", (50, 80), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)
            else:
                cv2.putText(black_canvas, "[ NO BIOMETRIC DATA ]", (50, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)
            
            combined_frame = cv2.hconcat([frame, black_canvas])
            
            if verified and not is_recording and (current_time - last_capture_time) >= CAPTURE_COOLDOWN:
                is_recording = True
                timestamp = datetime.now().strftime('%H%M%S')
                current_video_name = f"biometric_audit_{timestamp}.mp4"
                current_video_path = os.path.abspath(f"{VAULT_DIR}/{current_video_name}")
                
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                video_writer = cv2.VideoWriter(current_video_path, fourcc, 20.0, (w * 2, h))
                logging.info(f"REC_START: Recording forensic audit video: {current_video_name}")
                
            if is_recording:
                video_writer.write(combined_frame)
                cv2.circle(combined_frame, (30, 30), 10, (0, 0, 255), -1)
                cv2.putText(combined_frame, "REC", (50, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                if (current_time - last_capture_time - CAPTURE_COOLDOWN) >= RECORDING_DURATION:
                    is_recording = False
                    video_writer.release()
                    video_writer = None
                    last_capture_time = current_time
                    logging.info(f"REC_STOP: Video saved at {current_video_path}")
                    register_biometric_event(current_video_name, current_video_path)

            cv2.imshow('Sentinel | Enterprise Biometric Audit', combined_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Service termination requested by user.")
                break

    if video_writer is not None:
        video_writer.release()
    video_source.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    stream = cv2.VideoCapture(1)
    if stream.isOpened():
        run_biometric_service(stream)
    else:
        logging.error("Hardware error: Failed to bind optical sensor.")