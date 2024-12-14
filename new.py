import cv2
import numpy as np
from tkinter import *
from tkinter import messagebox, filedialog, ttk
from datetime import datetime
import pytz
import pandas as pd
import mysql.connector

class vehicle:
    def __init__(self,root):
        self.root = root
        self.root.geometry("850x550+400+150")
        self.root.title("Real Time Traffic Management System")

        global cars

        self.var_count = StringVar()
        self.var_date = StringVar()
        self.var_time = StringVar()
        self.var_filepath = StringVar()

        title_lbl = Label(text="Traffic Management System", font=("times new roman", 40, "bold"), bg="lightblue", fg="black")
        title_lbl.place(x=0, y=0, width=850, height=70)

        main_frame = Frame(bd=1, bg="lightblue")
        main_frame.place(x=0, y=70, width=250, height=480)

        main1_frame = Frame(bd=1, bg="white")
        main1_frame.place(x=0, y=70, width=850, height=60)


        b1 = Button(main1_frame, text="Start video",font=('Verdana 12 bold', 15 , "bold"), command=self.start)
        b1.place(x=350, y=10)

        b2 = Button(main_frame, text="Export all data", font=('Verdana 12 bold', 15, "bold"),command=self.exprt_data)
        b2.place(x=45, y=90)

        b3 = Button(main_frame, text="Delete all data from database", font=('Verdana 12 bold', 12 , "bold"), command=self.delete_data)
        b3.place(x=10, y=280)

        b4 = Button(main_frame, text="Select video", font=('Verdana 12 bold', 15, "bold"),command=self.openFile)
        b4.place(x=55, y=180)

        b5 = Button(main_frame, text="EXIT", font=('Verdana 12 bold', 15, "bold"), command=self.Close)
        b5.place(x=90, y=380)

        IST = pytz.timezone('Asia/Kolkata')

        label_date_now = Label(main1_frame,text="Current Date", font=('Verdana 12 bold', 20 , "bold"),bg="white")
        label_date_now.place(x=30, y=10)

        label_time_now = Label(main1_frame,text="Current Time", font=('Verdana 12 bold', 20 , "bold"),bg="white")
        label_time_now.place(x=650, y=10)

        # label_date = Label(text="Date", font='Verdana 11')
        # label_date.place(x=380, y=15)
        # label_dateformat = Label(text="[dd-mm-yyyy]", font='Verdana 7')
        # label_dateformat.place(x=420, y=18)

        left_frame = LabelFrame(root, bd=2, bg="white", relief=RIDGE, text="ALL DATA DISPLAY",
                                font=("times new roman", 15 , "bold"))
        left_frame.place(x=260, y=140, width=570, height=400)

        table_frame = Frame(left_frame, bd=2, bg="white", relief=RIDGE)
        table_frame.place(x=10, y=10, width=540, height=360)

        scroll_x = ttk.Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = ttk.Scrollbar(table_frame, orient=VERTICAL)

        self.student_table = ttk.Treeview(table_frame, column=("date", "time", "count"),xscrollcommand=scroll_x.set, yscrollcommand=scroll_y.set)

        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y)
        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        self.student_table.heading("date", text="DATE")
        self.student_table.heading("time", text="TIME")
        self.student_table.heading("count", text="COUNT OF CARS")
        self.student_table["show"] = "headings"

        self.student_table.column("date", width=100)
        self.student_table.column("time", width=100)
        self.student_table.column("count", width=100)

        self.student_table.pack(fill=BOTH, expand=1)
        self.fetch_data()


        def update_clock():
            raw_TS = datetime.now(IST)
            date_now = raw_TS.strftime("%d %b %Y")
            time_now = raw_TS.strftime("%H:%M:%S %p")
            formatted_now = raw_TS.strftime("%d-%m-%Y")
            label_date_now.config(text=date_now)
            # label_date_now.after(500, update_clock)
            label_time_now.config(text=time_now)
            label_time_now.after(1000, update_clock)
            self.var_date = str(date_now)
            self.var_time = str(time_now)
            return formatted_now

        update_clock()

    def openFile(self):
        filepath = filedialog.askopenfilename(initialdir='D:\\Projects ALL\\vehicle detection mini project',
                                              title="Open file okay?",
                                              filetypes=(("all files", "*.*"),("text files", "*.txt")))

        self.var_filepath = filepath


    def start(self):
        self.openFile()
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

        cap = cv2.VideoCapture(self.var_filepath)

        cap.set(4, 1920)
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
                contour_valid = (w >= min_contour_width) and (h >= min_contour_height)

                if not contour_valid:
                    continue
                cv2.rectangle(frame1, (x - 10, y - 10), (x + w + 10, y + h + 10), (255, 0, 0), 2)

                cv2.line(frame1, (0, line_height), (1500, line_height), (0, 255, 0), 2)
                centrolid = get_centrolid(x, y, w, h)
                matches.append(centrolid)
                cv2.circle(frame1, centrolid, 5, (0, 255, 0), -1)
                cx, cy = get_centrolid(x, y, w, h)
                for (x, y) in matches:
                    if y < (line_height + offset) and y > (line_height - offset):
                        cars = cars + 1
                        matches.remove((x, y))

            # lbl_count=Label(frame1,text="Total cars detected",font=("times new roman", 30, "bold"),bg="white", fg="black")
            # lbl_count.place(x=20,y=300,width=50,height=50)

            cv2.putText(frame1, "Total Vehicles Detected: " + str(cars), (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 2,
                        (255, 255, 255), 2)

            cv2.putText(frame1, "Press 'Q' to STOP", (500, 500), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (255, 255, 255), 2)

            cv2.imshow("Vehicle Detection", frame1)

            cv2.imshow("Difference", th)

            self.var_count = str(cars)

            # if cars == 30:
            #     cv2.putText(frame1, "cars limit reached", (100, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color="red",
            #                 thickness=2)


            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.add_data()
                break
            frame1 = frame2
            ret, frame2 = cap.read()
        cv2.destroyAllWindows()
        cap.release()



    def fetch_data(self):
        conn = mysql.connector.connect(host="localhost",
                                       username="root",
                                       password="Delldell123",
                                       database="traffic_management")
        my_cursor = conn.cursor()
        my_cursor.execute("select * from new_table")
        data = my_cursor.fetchall()

        if len(data) != 0:
            self.student_table.delete(*self.student_table.get_children())
            for i in data:
                self.student_table.insert("", END, values=i)
            conn.commit()
        conn.close()


    def add_data(self):
        try:
            conn = mysql.connector.connect(username="root",
                                           password="Delldell123",
                                           host="localhost",
                                           database="traffic_management")
            mycursor = conn.cursor()
            mycursor.execute("insert into new_table (date,time,count) values(%s,%s,%s)", (self.var_date,self.var_time,self.var_count,))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Record saved", parent=self.root)
        except Exception as es:
            messagebox.showerror("Error", f"Due to: {str(es)}", parent=self.root)



    def exprt_data(self):
        db = mysql.connector.connect(username='root',
                                     password='Delldell123',
                                     host='localhost',
                                     database='traffic_management')
        sql = "SELECT * FROM traffic_management.new_table;"
        df=pd.read_sql(sql,db)
        df.head()
        df.to_excel("Real time traffic management data.xlsx",index=False)
        messagebox.showinfo("Success","Data Exported Successfully")
        db.close()



    def delete_data(self):
            try:
                delete = messagebox.askyesno("Delete", "Do you want to Delete all data from database?", parent=self.root)
                if delete > 0:
                    conn = mysql.connector.connect(username='root',
                                                   password='Delldell123',
                                                   host='localhost',
                                                   database='traffic_management')
                    mycursor = conn.cursor()
                    sql = "DELETE FROM new_table;"
                    mycursor.execute(sql)
                else:
                    if not delete:
                        return

                conn.commit()
                conn.close()
                messagebox.showinfo("Delete", "Successfully Deleted!", parent=self.root)
            except Exception as es:
                messagebox.showerror("Error", f"Due to: {str(es)}", parent=self.root)

    def Close(self):
        root.destroy()

if __name__ == "__main__":
    root=Tk()
    obj=vehicle(root)
    root.mainloop()