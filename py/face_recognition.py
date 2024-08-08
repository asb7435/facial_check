import cv2
import dlib
import numpy as np

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("lib/shape_predictor_68_face_landmarks.dat")
face_rec_model = dlib.face_recognition_model_v1("lib/dlib_face_recognition_resnet_model_v1.dat")

def get_face_encodings(image):
    faces = detector(image, 1)
    encodings = []
    for face in faces:
        shape = predictor(image, face)
        face_encoding = face_rec_model.compute_face_descriptor(image, shape)
        encodings.append(np.array(face_encoding))
    return encodings

def compare_faces(known_encodings, face_encoding, tolerance=0.6):
    return np.linalg.norm(known_encodings - face_encoding, axis=1) <= tolerance
