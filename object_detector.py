from ultralytics import YOLO

model = YOLO('yolov8l.pt')

results = model('./assets/test_image2.jpg')

results[0].show()