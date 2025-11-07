import cv2
from ultralytics import YOLO
from tracker import CentroidTracker
import numpy as np

# Initialize
model = YOLO('yolov8n.pt')
tracker = CentroidTracker()

# Open video
video_path = './assets/test_video2.mp4'
cap = cv2.VideoCapture(video_path)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Detect objects
    results = model(frame)
    
    # Extract centroids from detections
    detections = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        centroid_x = int((x1 + x2) / 2)
        centroid_y = int((y1 + y2) / 2)
        detections.append([centroid_x, centroid_y])
    
    # Update tracker
    objects = tracker.update(np.array(detections))
    
    # Draw bounding boxes and IDs
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
    
    # Draw tracked object IDs
    for object_id, centroid in objects.items():
        text = f"ID {object_id}"
        cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
    
    # Display
    cv2.imshow('Tracking', frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()