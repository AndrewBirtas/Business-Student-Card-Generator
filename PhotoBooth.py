# import the necessary packages
from __future__ import print_function
from PIL import Image
from PIL import ImageTk
from tkinter import Toplevel, Canvas, messagebox, filedialog, Button, Tk, Label, LabelFrame, Entry, IntVar, StringVar, \
    OptionMenu, Checkbutton, Scale, NW, HORIZONTAL, DISABLED, NORMAL
from email_validator import validate_email, EmailNotValidError
import threading
import pymongo
import imutils
import cv2
import os
import datetime
import math
import numpy as np


class PhotoBoothApp:
    def __init__(self, vs, outputPath):
        # store the video stream object and output path, then initialize
        # the most recently read frame, thread for reading frames, and
        # the thread stop event
        self.vs = vs
        self.outputPath = "output"
        self.frame = None
        self.thread = None
        self.stopEvent = None
        # initialize the root window and image panel
        self.root = Tk()
        self.root.iconbitmap("Resources/card+id+id+card+identity+identity+card+icon+icon-1320196206727682853.ico")
        self.root.title("Card Generator")
        self.face_cascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
        self.root.resizable(False, False)
        self.panel = None

        # Frame Creation
        frame_form = LabelFrame(self.root, text="Date Personale", padx=5, pady=5, width=350, height=420)
        frame_form.grid_propagate(False)
        frame_form.grid(row=0, column=0, padx=10, pady=10)
        frame_video = LabelFrame(self.root, text="Captura Camera Web", padx=5, pady=5, width=500, height=420)
        frame_video.pack_propagate(False)
        frame_video.grid(row=0, column=1, padx=10, pady=10)
        frame_send = LabelFrame(self.root, text="Salvare & Generare", padx=5, pady=5, width=350, height=234)
        frame_send.grid_propagate(False)
        frame_send.grid(row=1, column=0, padx=10, pady=10)
        frame_image = LabelFrame(self.root, text="Editare Imagine", padx=5, pady=5, width=500, height=234)
        frame_image.grid_propagate(False)
        frame_image.grid(row=1, column=1, padx=10, pady=10)

        # --------------Frame Form--------------
        # Label Init
        nume_label = Label(frame_form, text="Nume: ").grid(row=0, column=0, sticky="w")
        nume_empty_label = Label(frame_form, text="").grid(row=1, column=0)
        prenume_label = Label(frame_form, text="Prenume: ").grid(row=2, column=0, sticky="w")
        prenume_empty_label = Label(frame_form, text="").grid(row=3, column=0)
        cnp_label = Label(frame_form, text="CNP: ").grid(row=4, column=0, sticky="w")
        cnp_empty_label = Label(frame_form, text="").grid(row=5, column=0)
        matr_label = Label(frame_form, text="Nr. Matricol: ").grid(row=6, column=0, sticky="w")
        matr_empty_label = Label(frame_form, text="").grid(row=7, column=0)
        email_label = Label(frame_form, text="Email: ").grid(row=8, column=0, sticky="w")
        email_empty_label = Label(frame_form, text="").grid(row=9, column=0)
        uni_label = Label(frame_form, text="Universitate: ").grid(row=10, column=0, sticky="w")
        uni_empty_label = Label(frame_form, text="").grid(row=11, column=0)
        fac_label = Label(frame_form, text="Facultate: ").grid(row=12, column=0, sticky="w")
        fac_empty_label = Label(frame_form, text="").grid(row=13, column=0)
        an_label = Label(frame_form, text="An: ").grid(row=14, column=0, sticky="w")
        an_empty_label = Label(frame_form, text="").grid(row=15, column=0)

        # Entry Init
        matr_reg = (self.root.register(self.validate_matr), '%P')
        cnp_reg = (self.root.register(self.validate_cnp), '%P')
        email_reg = (self.root.register(self.validate_email), '%P')
        self.nume_entry = Entry(frame_form, width=40, borderwidth=5)
        self.nume_entry.grid(row=0, column=1)
        self.prenume_entry = Entry(frame_form, width=40, borderwidth=5)
        self.prenume_entry.grid(row=2, column=1)
        self.cnp_entry = Entry(frame_form, width=40, borderwidth=5, validate="all", validatecommand=cnp_reg)
        self.cnp_entry.grid(row=4, column=1)
        self.cnp_empty_entry = Label(frame_form, text="", fg="red")
        self.cnp_empty_entry.grid(row=5, column=1)
        self.matr_entry = Entry(frame_form, width=40, borderwidth=5, validate="all", validatecommand=matr_reg)
        self.matr_entry.grid(row=6, column=1)
        self.matr_empty_entry = Label(frame_form, text="", fg="red")
        self.matr_empty_entry.grid(row=7, column=1)
        self.email_entry = Entry(frame_form, width=40, borderwidth=5, validate="all", validatecommand=email_reg)
        self.email_entry.grid(row=8, column=1)
        self.email_empty_entry = Label(frame_form, text="", fg="red")
        self.email_empty_entry.grid(row=9, column=1)

        # Dropdown Init
        self.var_uni = StringVar()
        self.var_fac = StringVar()
        self.var_an = StringVar()
        uni_drop = OptionMenu(frame_form, self.var_uni, "UPT", "UVT", "UBB", command=lambda x: self.pick(frame_form))
        uni_drop.grid(row=10, column=1, sticky="ew")
        print(self.var_uni.get())
        self.fac_drop = OptionMenu(frame_form, self.var_fac, "").grid(row=12, column=1, sticky="ew")
        an_drop = OptionMenu(frame_form, self.var_an, "1", "2", "3", "4").grid(row=14, column=1, sticky="w")

        # --------------Frame Save & Export--------------
        # Label Init
        imagine_label = Label(frame_send, text="Imagine de fundal: ").grid(row=0, column=0, sticky="w")
        imagine_empty_label = Label(frame_send, text="").grid(row=1, column=0)
        save_db_label = Label(frame_send, text="Salvare DB: ").grid(row=2, column=0, sticky="w")
        save_empty_label = Label(frame_send, text="").grid(row=3, column=0)
        generate_label = Label(frame_send, text="Generare card: ").grid(row=4, column=0, sticky="w")
        generate_empty_label = Label(frame_send, text="").grid(row=5, column=0)
        # Button Init
        search = Button(frame_send, text="Cauta Imagine", padx=5, pady=5, command=lambda: self.search_im(frame_send))
        search.grid(row=0, column=1)
        self.photo_save = ImageTk.PhotoImage(Image.open("Resources/save.png").resize((75, 50)))
        save_btn = Button(frame_send, image=self.photo_save, command=self.db_save)
        save_btn.grid(row=2, column=1)
        self.photo_generate = ImageTk.PhotoImage(
            Image.open("Resources/card+id+id+card+identity+identity+card+icon+icon-1320196206727682853.png").resize(
                (75, 50)))
        self.generate_btn = Button(frame_send, image=self.photo_generate, padx=5, pady=5, state=DISABLED, command=self.generate)
        self.generate_btn.grid(row=4, column=1)

        # Descriptions
        self.var_preview = IntVar()
        preview = Checkbutton(frame_send, text="Previzualizare", variable=self.var_preview)
        preview.grid(row=4, column=2)

        # --------------Frame Webcam--------------
        # Inits
        web_btn = Button(frame_video, text="Activare camera web", command=self.Open_cam).pack()
        self.black_placeholder = ImageTk.PhotoImage(Image.open("Resources/placeholder.png").resize((400, 300)))
        self.web_feed = Label(frame_video, image=self.black_placeholder)
        self.web_feed.pack()
        self.take_btn = Button(frame_video, text="Faceti poza", padx=40, pady=40, state=DISABLED, command=self.takeSnapshot)
        self.take_btn.pack()

        # --------------Frame Image--------------
        # Inits
        self.black_placeholder_image = ImageTk.PhotoImage(Image.open("Resources/placeholder.png").resize((200, 200)))
        self.image_feed = Label(frame_image, image=self.black_placeholder_image)
        self.image_feed.grid(row=0, column=0, rowspan=4)
        self.filter1 = Button(frame_image, text="Blur", padx=5, pady=5, state=DISABLED, command=self.fil1)
        self.filter1.grid(row=0, column=1, padx=10)
        self.filter2 = Button(frame_image, text="Sepia", padx=5, pady=5, state=DISABLED, command=self.fil2)
        self.filter2.grid(row=0, column=2)
        self.filter3 = Button(frame_image, text="Gray", padx=5, pady=5, state=DISABLED, command=self.fil3)
        self.filter3.grid(row=0, column=3, padx=10)
        self.filter4 = Button(frame_image, text="Sharpening", padx=5, pady=5, state=DISABLED, command=self.fil4)
        self.filter4.grid(row=0, column=4)
        selected_filter = Label(frame_image, text="Selected filter:").grid(row=1, column=1, columnspan=4)
        self.selected_filter_name = Label(frame_image, text="No Filter Selected")
        self.selected_filter_name.grid(row=2, column=1, columnspan=4)

        self.root.wm_protocol("WM_DELETE_WINDOW", self.onClose)

    def validate_matr(self, key):
        if key.isdigit() and len(key) < 6:
            print(key)
            self.matr_empty_entry["text"] = ""
            return True
        elif key is "" and len(key) < 6:
            print(key)
            self.matr_empty_entry["text"] = ""
            return True
        else:
            print(key)
            self.matr_empty_entry["text"] = "Numarul matricol este format din 5 cifre"
            return False

    def validate_email(self, key):
        print(key)
        try:
            valid = validate_email(key)
            self.email_empty_entry["text"] = ""
        except EmailNotValidError as e:
            self.email_empty_entry["text"] = "Invalid email"
        return True

    def validate_cnp(self, key):
        if key.isdigit() and len(key) < 14:
            print(key)
            self.cnp_empty_entry["text"] = ""
            return True
        elif key is "" and len(key) < 14:
            print(key)
            self.cnp_empty_entry["text"] = ""
            return True
        else:
            print(key)
            self.cnp_empty_entry["text"] = "CNP este format din 13 cifre"
            return False

    def pick(self, ff):

        if self.var_uni.get() == "UPT":
            fac_drop = OptionMenu(ff, self.var_fac, "CTI", "IS", "Info").grid(row=12, column=1, sticky="ew")
        else:
            fac_drop = OptionMenu(ff, self.var_fac, "Mate-Info", "Stiinte", "Arte").grid(row=12, column=1, sticky="ew")

    def search_im(self, fs):
        self.root.filename = filedialog.askopenfilename(initialdir="Resources", title="Select a File", filetypes=(("png files", "*.png"), ("all files", "*.*")))
        # self.file = Label(fs, text=self.root.filename)
        # self.file.grid(row=0, column=2)

    def get_varsta(self):
        an = self.cnp_entry.get()[1:3]
        an = "19" + an
        luna = self.cnp_entry.get()[3:5]
        if int(luna) > 12:
            return 0
        zi = self.cnp_entry.get()[5:7]
        if int(zi) > 31:
            return 0
        birth = datetime.datetime(int(an), int(luna), int(zi), 0, 0, 0)
        today = datetime.datetime.utcnow()
        varsta = today - birth
        varsta_in_days = varsta.days
        varsta_final = varsta_in_days / 365
        print(varsta_final)
        return math.floor(varsta_final)

    def db_save(self):
        myclient = pymongo.MongoClient("mongodb+srv://Andrew:kCkQ0U18X6jemlHK@apppractica.bxrt8.mongodb.net/AppPractica?retryWrites=true&w=majority")
        mydb = myclient["AppPractica"]
        mycol = mydb["Data Set"]
        nume = self.nume_entry.get()
        prenume = self.prenume_entry.get()
        email = self.email_entry.get()
        matr = self.matr_entry.get()
        uni = self.var_uni.get()
        fac = self.var_fac.get()
        an = self.var_an.get()
        if nume is not "" and prenume is not "" and self.cnp_entry.get() is not "" and email is not "" and matr is not "" and uni is not "" and fac is not "" and an is not "":
            varsta = self.get_varsta()
            if varsta == 0:
                messagebox.showerror("Invalid save", "Month must be between 1-12 and Days between 1-31 in CNP")
            else:
                mydict = {"name": nume, "surname": prenume, "age": varsta, "email": email, "number": matr, "university": uni, "department": fac, "year": an}
                mycol.insert_one(mydict)
                messagebox.showinfo("Success!", "Data is stored into the database")
        else:
            messagebox.showerror("Invalid save", "Please provide all information before saving into the database")

    def Open_cam(self):
        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

    def videoLoop(self):
        try:
            while not self.stopEvent.is_set():
                self.frame = self.vs.read()
                self.frame = cv2.flip(self.frame, 1)
                self.frame = imutils.resize(self.frame, width=300, height=400)
                self.frame_gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                face = self.face_cascade.detectMultiScale(self.frame_gray, 1.1, 4)

                for (x, y, w, h) in face:
                    if 60 < x < 120:
                        self.take_btn['state'] = NORMAL
                    else:
                        self.take_btn['state'] = DISABLED

                image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(image)
                image = ImageTk.PhotoImage(image.resize((400, 300)))

                if self.web_feed is None:
                    self.web_feed = Label(image=image)
                    self.web_feed.image = image
                    self.web_feed.pack()
                else:
                    self.web_feed.configure(image=image)
                    self.web_feed.image = image
        except RuntimeError as e:
            print("[INFO] caught a RuntimeError")

    def takeSnapshot(self):
        print(self.nume_entry.get())
        if self.nume_entry.get() == "":
            messagebox.showwarning("WARNING", "Please specify your name in order to save a image of yourself!!!")
        else:
            filename = "{}.jpg".format(self.nume_entry.get())
            filename2 = "{}.jpg".format(self.nume_entry.get() + "_filtered")
            p = os.path.sep.join((self.outputPath, filename))
            p2 = os.path.sep.join((self.outputPath, filename2))
            cv2.imwrite(p, self.frame.copy())
            cv2.imwrite(p2, self.frame.copy())
            print("[INFO] saved {}".format(filename))
            print("[INFO] saved {}".format(filename2))
            image = ImageTk.PhotoImage(Image.open(f"output/{self.nume_entry.get()}.jpg").resize((200, 200)))
            self.image_feed.configure(image=image)
            self.image_feed.image = image
            self.filter1['state'] = NORMAL
            self.filter2['state'] = NORMAL
            self.filter3['state'] = NORMAL
            self.filter4['state'] = NORMAL
            self.generate_btn['state'] = NORMAL

    def generate(self):
        print(self.var_preview.get())
        nume = self.nume_entry.get()
        prenume = self.prenume_entry.get()
        email = self.email_entry.get()
        matr = self.matr_entry.get()
        uni = self.var_uni.get()
        fac = self.var_fac.get()
        an = self.var_an.get()
        if nume is not "" and prenume is not "" and self.cnp_entry.get() is not "" and email is not "" and matr is not "" and uni is not "" and fac is not "" and an is not "":
            varsta = self.get_varsta()
            if varsta == 0:
                messagebox.showerror("Invalid generate", "Month must be between 1-12 and Days between 1-31 in CNP")
            else:
                gui = Toplevel(self.root)
                # self.bk_img = ImageTk.PhotoImage(Image.open(self.root.filename))
                self.a = Canvas(gui, width=300, height=200)
                # bkg_label = Label(gui, image=self.bk_img)
                # bkg_label.place(x=0, y=0, relwidth=1, relheight=1)
                self.a.pack()

                self.gen_image = ImageTk.PhotoImage(Image.open(f"output/{self.nume_entry.get()}_filtered.jpg").resize((100, 100)))
                self.a.create_image(10, 10, image=self.gen_image, anchor=NW)
                self.a.create_text(200, 10, fill="darkblue", font="Times 9 bold", text=self.nume_entry.get())
                self.a.create_text(200, 30, fill="darkblue", font="Times 9 bold", text=self.prenume_entry.get())
                self.a.create_text(200, 50, fill="darkblue", font="Times 9 bold", text=varsta)
                self.a.create_text(200, 70, fill="darkblue", font="Times 9 bold", text=self.matr_entry.get())
                self.a.create_text(200, 90, fill="darkblue", font="Times 9 bold", text=self.email_entry.get())
                self.a.create_text(200, 110, fill="darkblue", font="Times 9 bold", text=self.var_uni.get())
                self.a.create_text(200, 130, fill="darkblue", font="Times 9 bold", text=self.var_fac.get())
                self.a.create_text(200, 150, fill="darkblue", font="Times 9 bold", text=self.var_an.get())
                self.a.update()
                self.a.postscript(file="Generated.eps")
                gen = Image.open("Generated.eps")
                gen.save("Generatate.png", "png")

                if self.var_preview.get() == 0:
                    gui.destroy()
                    messagebox.showinfo("Success!", "Card is successfully generated!")

        else:
            messagebox.showerror("Invalid generate", "Please provide all information before generating")

    def fil1(self):
        self.selected_filter_name['text'] = "Blur"
        path = f"output/{self.nume_entry.get()}.jpg"
        print(path)
        blur1 = cv2.imread(path)
        blur2 = cv2.GaussianBlur(blur1, (13, 13), 1)
        filename = "{}.jpg".format(self.nume_entry.get() + "_filtered")
        p = os.path.sep.join((self.outputPath, filename))
        # save the file
        cv2.imwrite(p, blur2)
        print("[INFO] saved {}".format(filename))

        image = ImageTk.PhotoImage(Image.open(f"output/{self.nume_entry.get()}_filtered.jpg").resize((200, 200)))
        self.image_feed.configure(image=image)
        self.image_feed.image = image

    def fil2(self):
        self.selected_filter_name['text'] = "Sepia"
        path = f"output/{self.nume_entry.get()}.jpg"
        print(path)
        kernel = np.array([[0.272, 0.534, 0.131],
                           [0.349, 0.686, 0.168],
                           [0.393, 0.769, 0.189]])
        sepia1 = cv2.imread(path)
        sepia2 = cv2.filter2D(sepia1, -1, kernel)
        filename = "{}.jpg".format(self.nume_entry.get() + "_filtered")
        p = os.path.sep.join((self.outputPath, filename))
        # save the file
        cv2.imwrite(p, sepia2)
        print("[INFO] saved {}".format(filename))

        image = ImageTk.PhotoImage(Image.open(f"output/{self.nume_entry.get()}_filtered.jpg").resize((200, 200)))
        self.image_feed.configure(image=image)
        self.image_feed.image = image

    def fil3(self):
        self.selected_filter_name['text'] = "Gray"
        path = f"output/{self.nume_entry.get()}.jpg"
        print(path)
        gray1 = cv2.imread(path)
        gray2 = cv2.cvtColor(gray1, cv2.COLOR_BGR2GRAY)
        filename = "{}.jpg".format(self.nume_entry.get() + "_filtered")
        p = os.path.sep.join((self.outputPath, filename))
        # save the file
        cv2.imwrite(p, gray2)
        print("[INFO] saved {}".format(filename))

        image = ImageTk.PhotoImage(Image.open(f"output/{self.nume_entry.get()}_filtered.jpg").resize((200, 200)))
        self.image_feed.configure(image=image)
        self.image_feed.image = image

    def fil4(self):
        self.selected_filter_name['text'] = "Sharpening"
        path = f"output/{self.nume_entry.get()}.jpg"
        print(path)
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharp1 = cv2.imread(path)
        sharp2 = cv2.filter2D(sharp1, -1, kernel)
        filename = "{}.jpg".format(self.nume_entry.get() + "_filtered")
        p = os.path.sep.join((self.outputPath, filename))
        # save the file
        cv2.imwrite(p, sharp2)
        print("[INFO] saved {}".format(filename))

        image = ImageTk.PhotoImage(Image.open(f"output/{self.nume_entry.get()}_filtered.jpg").resize((200, 200)))
        self.image_feed.configure(image=image)
        self.image_feed.image = image

    def onClose(self):
        # set the stop event, cleanup the camera, and allow the rest of
        # the quit process to continue
        print("[INFO] closing...")

        self.vs.stop()
        self.root.quit()
        self.stopEvent.set()
