pip install face_recognition opencv-python numpy pandas
import face_recognition
import cv2
import numpy as np
import pandas as pd
import os
from datetime import datetime

# Load known faces and their names
known_face_encodings = []
known_face_names = []

# Load all images from known_faces directory
for image_name in os.listdir('known_faces'):
    image = face_recognition.load_image_file(f'known_faces/{image_name}')
    image_encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(image_encoding)
    # Extract name from filename (remove extension)
    known_face_names.append(os.path.splitext(image_name)[0])

# Initialize attendance DataFrame
attendance_df = pd.DataFrame(columns=["Name", "Time"])

# Initialize webcam
video_capture = cv2.VideoCapture(0)

# Process each frame from webcam
while True:
    ret, frame = video_capture.read()

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR (OpenCV) to RGB (face_recognition)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Detect faces in the frame
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # Loop through all detected faces
    for face_encoding in face_encodings:
        # Compare detected face with known faces
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"

        # Find the best match
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)

        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        # Mark attendance if recognized
        if name != "Unknown":
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            if name not in attendance_df["Name"].values:
                attendance_df = attendance_df.append({"Name": name, "Time": current_time}, ignore_index=True)

        # Display the name on the video frame
        for (top, right, bottom, left) in face_locations:
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

    # Show the video frame
    cv2.imshow('Video', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Save the attendance to a CSV file
attendance_df.to_csv('attendance.csv', index=False)

# Release the webcam and close windows
video_capture.release()
cv2.destroyAllWindows()