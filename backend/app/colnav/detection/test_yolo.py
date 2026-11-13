from ultralytics import YOLO
import torch

print("Loading YOLOv8 Nano...")

model = YOLO("yolov8n.pt")

print("Model loaded successfully!")

print("Execution device: CPU")

print("CUDA available:", torch.cuda.is_available())

print("\nModel classes:")

print(model.names)