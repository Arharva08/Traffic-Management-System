from ultralytics import YOLO
import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread

def detect_traffic_objects(ip_vid, op_vid):
    model = YOLO('yolov8n.pt') 
    cap = cv2.VideoCapture(ip_vid)

    if not cap.isOpened():
        messagebox.showerror("Error", "Could not open video file.")
        return

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(op_vid, fourcc, fps, (width, height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)

        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist()) 
                conf = box.conf[0].item()  
                cls = int(box.cls[0].item())  
                label = f"{model.names[cls]} ({conf:.2f})"

                if model.names[cls] in ["car", "bus", "truck", "motorcycle", "bicycle", "person", "stop sign"]:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        out.write(frame) 
        cv2.imshow("Traffic Object Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

    messagebox.showinfo("Success", "Object detection completed successfully!")

def select_ip_vid():
    input_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mkv")])
    if input_path:
        ip_vid_var.set(input_path)

def select_op_vid():
    output_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
    if output_path:
        op_vid_var.set(output_path)

def start_detection():
    input_path = ip_vid_var.get()
    output_path = op_vid_var.get()

    if not input_path or not output_path:
        messagebox.showwarning("Warning", "Please select both input and output video paths.")
        return

    detection_thread = Thread(target=detect_traffic_objects, args=(input_path, output_path))
    detection_thread.start()

root = tk.Tk()
root.title("Traffic Object Detection")
root.geometry("500x300")
root.configure(bg="#f4f4f9")

header_label = tk.Label(root, text="Traffic Object Detection", font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=10)
header_label.pack(fill=tk.X)

frame = tk.Frame(root, bg="#f4f4f9")
frame.pack(pady=20)

ip_vid_var = tk.StringVar()
op_vid_var = tk.StringVar()

tk.Label(frame, text="Input Video:", font=("Arial", 12), bg="#f4f4f9").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
input_video_entry = tk.Entry(frame, textvariable=ip_vid_var, width=40, font=("Arial", 10))
input_video_entry.grid(row=0, column=1, padx=10, pady=5)
tk.Button(frame, text="Browse", command=select_ip_vid, bg="#3498db", fg="white", font=("Arial", 10)).grid(row=0, column=2, padx=10, pady=5)

tk.Label(frame, text="Output Video:", font=("Arial", 12), bg="#f4f4f9").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
output_video_entry = tk.Entry(frame, textvariable=op_vid_var, width=40, font=("Arial", 10))
output_video_entry.grid(row=1, column=1, padx=10, pady=5)
tk.Button(frame, text="Browse", command=select_op_vid, bg="#3498db", fg="white", font=("Arial", 10)).grid(row=1, column=2, padx=10, pady=5)

start_button = tk.Button(root, text="Start Detection", command=start_detection, bg="#27ae60", fg="white", font=("Arial", 14), pady=10)
start_button.pack(pady=20)

root.mainloop()
