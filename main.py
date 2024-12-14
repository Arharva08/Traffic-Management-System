import cv2
import numpy as np
from tkinter import *
from time import strftime

min_contour_width = 50
min_contour_height = 50
offset = 3
line_height = 500
matches = []
cars = 0

def get_centrolid(x, y, w, h):
    x1 = int(w / 2)
    y1 = int(h / 2)

    cx = x + x1
    cy = y + y1
    return cx, cy

def my_time():
    time_string = strftime("%H:%M:%S %p")
    l1.config(time_string)

def end():
    exit()

def start():
    global cars
    cap = cv2.VideoCapture('video.mp4')
    cap.set(3, 1920)
    cap.set(4, 1080)

    if cap.isOpened():
        ret, frame1 = cap.read()
    else:
        ret = False

    ret, frame1 = cap.read()
    ret, frame2 = cap.read()


    while ret:
        d = cv2.absdiff(frame1, frame2)
        grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)

        blur = cv2.GaussianBlur(grey, (5, 5), 0)

        ret, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(th, np.ones((3, 3)))
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))

        closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
        contours, h = cv2.findContours(
            closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for (i, c) in enumerate(contours):
            (x, y, w, h) = cv2.boundingRect(c)
            contour_valid = (w >= min_contour_width) and (
                    h >= min_contour_height)

            if not contour_valid:
                continue
            cv2.rectangle(frame1, (x - 10, y - 10), (x + w + 10, y + h + 10), (255, 0, 0), 2)

            cv2.line(frame1, (0, line_height), (1200, line_height), (0, 255, 0), 2)
            centrolid = get_centrolid(x, y, w, h)
            matches.append(centrolid)
            cv2.circle(frame1, centrolid, 5, (0, 255, 0), -1)
            cx, cy = get_centrolid(x, y, w, h)
            for (x, y) in matches:
                if y < (line_height + offset) and y > (line_height -offset):
                    cars = cars + 1
                    matches.remove((x, y))

        # lbl_count=Label(frame1,text="Total cars detected",font=("times new roman", 30, "bold"),bg="white", fg="black")
        # lbl_count.place(x=20,y=300,width=50,height=50)
        cv2.putText(frame1, "Total Cars Detected: " + str(cars), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 2,
                    (255,255,255), 2)

        cv2.imshow("Vehicle Detection", frame1)

        # if cars == 30:
        #     cv2.putText(frame1, "cars limit reached", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color="red",
        #                 thickness=2)

        #b2=Button(frame1,text="STOP",command=end)
        #b2.place(x=200,y=50)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        frame1 = frame2
        ret, frame2 = cap.read()
    cv2.destroyAllWindows()
    cap.release()


root=Tk()
root.geometry("800x470+400+150")
title_lbl=Label(text="Traffic Managment System",font=("times new roman",30,"bold"),bg="white",fg="black")
title_lbl.place(x=0,y=0,width=800,height=45)
l1 = Label(root,font=("times new roman",30,"bold"),bg="yellow")
l1.place(x=0,y=50)
my_time()
b1=Button(root,text="Start video",command=start)
b1.place(x=200,y=250)
#cv2.createButton("STOP", end, None, cv2.QT_PUSH_BUTTON, 0)
b2 = Button(root,text="END",command=end)
b2.place(x=200,y=280)
root.mainloop()



