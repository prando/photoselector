try:
    from Tkinter import *
except ImportError:
    from tkinter import *
try:
    import tkMessageBox
except ImportError:
    from tkinter import messagebox as tkMessageBox
try:
    import tkFileDialog
except ImportError:
    from tkinter import filedialog as tkFileDialog

import os

from PIL import Image, ImageTk

class App:
    def __init__(self, master):

        # Set NULL references to image & label objects at APP init
        self.curimage = None
        self.oldimlabel = None
        self.oldtxtlabel = None
        self.curimgidx = 0

        # Initialize empty lists to denote loaded, selected, rejected images
        self.loaded = []
        self.selected = []
        self.rejected = []
        self.tentative = []
        # Use a string var and anchor it to a text label. Any change to string var will
        # be displayed by the text label.
        self.textstring = StringVar()
        self.photoindex = StringVar()

        # Image load path
        self.file_path_str = []
        # Selected image list file path
        self.out_file_path_str = []

        # Setup a frame (child of master) to display buttons
        self.frame = Frame (master)
        # Show frame.
        self.frame.pack()

        # Setup a frame (child of Frame) to display image
        self.imframe = Frame (self.frame, relief=SUNKEN)
        # Show frame.
        self.imframe.pack(side=BOTTOM)

        # Setup a frame (child of imrame) to display image
        self.txtboxframe = Frame (self.imframe, relief=SUNKEN)
        # Show frame.
        self.txtboxframe.pack(side=BOTTOM)

        # Setup buttons with actions triggering command=$$$ function.
        self.loadbutton = Button (self.frame, text="LOAD", command=self.loadpic)
        self.loadbutton.pack(side=LEFT)

        self.firstbutton = Button (self.frame, text="FIRST", command=self.firstpic)
        self.firstbutton.pack(side=LEFT)

        self.lastbutton = Button (self.frame, text="LAST", command=self.lastpic)
        self.lastbutton.pack(side=LEFT)

        self.quitbutton = Button (self.frame, text="SAVE", command=self.saveprog)
        self.quitbutton.pack(side=RIGHT)
        
        self.quitbutton = Button (self.frame, text="QUIT", command=self.quitprog)
        self.quitbutton.pack(side=RIGHT)

        self.selectbutton = Button (self.frame, text="SELECT", command=self.selectpic, height=10, width=10)
        self.selectbutton.pack(side=LEFT)

        self.nextbutton = Button (self.frame, text="NEXT", command=self.nextpic)
        self.nextbutton.pack(side=LEFT)

        self.previousbutton = Button (self.frame, text="PREVIOUS", command=self.previouspic)
        self.previousbutton.pack(side=LEFT)

        self.rotatebutton = Button (self.frame, text="ROTATE LEFT", command=self.rotatepicleft)
        self.rotatebutton.pack(side=RIGHT)

        self.rotatebutton = Button (self.frame, text="ROTATE RIGHT", command=self.rotatepicright)
        self.rotatebutton.pack(side=RIGHT)

        # Setup a text label to show display image index and anchor it to a string var.
        # self.txtlabel = Label (self.imframe, textvar=self.textstring)
        # self.txtlabel.pack(side=BOTTOM)

        # Set up a label with entry to take input for Go to a particular photo
        self.gotolabel = Label (self.txtboxframe, textvar= self.textstring)
        self.gotolabel.pack(side=RIGHT)
        self.txtbox = Entry (self.txtboxframe, textvariable=self.photoindex, bd=1, width=4, justify=RIGHT)
        self.txtbox.bind('<Return>', self.get)
        self.txtbox.pack(side=LEFT)

        # self.gotobutton = Button (self.frame, text="GO TO", command=self.gotopicture)
        # self.gotobutton.pack(side=BOTTOM)

        # Note that the default pic is un-rotated. Used to toggle thumbnail
        # self.rotated = 0

    # Quit button action.
    def quitprog (self):
        # If selected list is not empty, prompt user for location to save list of selected images & append to it.
        self.saveprog()

        # Quit program.
        self.frame.quit ()

    def saveprog (self):
        # If selected list is not empty, prompt user for location to save list of selected images & append to it.

        if self.selected:
            res = tkMessageBox.askquestion ("Save Selected", "Do you want to save the selected photo list?")
            if res == 'yes':
                self.out_file_path_str = tkFileDialog.askdirectory (title='Choose target dir to store selected files')
                if not self.out_file_path_str:
                    tkMessageBox.showerror ("Error", "Choose valid dir")
                    self.saveprog()
                self.out_file_path_str = os.path.join (self.out_file_path_str, 'selected_photos.txt')
                with open (self.out_file_path_str, "a") as f:
                    for n in self.selected:
                        f.write (n+"\n")
            else:
                return

    # Select button action.
    def selectpic (self):
        # Handle error condition: No images loaded yet.
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # If selected, add to list if not previously added.
        if self.selectbutton ["text"] == "SELECT":
            if self.curimage not in self.selected:
                self.selected.append (self.curimage)
                self.selectbutton ["text"] = "UNSELECT"
            else:
                tkMessageBox.showwarning ("Warning", "Already selected!")
        else:
            self.selected.remove (self.curimage)
            self.selectbutton ["text"] = "SELECT"

    def showimage (self):

        # if self.rotated:
        #     self.image.thumbnail ((648, 648), Image.ANTIALIAS)
        # else:
        #     self.image.thumbnail ((648, 648), Image.ANTIALIAS)
        self.image.thumbnail ((648, 648), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage (self.image)
        self.imlabel = Label (self.imframe, image=photo, height=648, width=648)
        self.imlabel.image = photo
        self.imlabel.pack (side=BOTTOM)
        if self.oldimlabel is not None:
            self.oldimlabel.destroy ()
        # Save a reference to image label (enables destroying to repaint)
        self.oldimlabel = self.imlabel

    def rotatepicleft (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return

        self.image = self.image.rotate (90, expand=True)
        # self.rotated = self.rotated ^ 1
        self.showimage ()

    def rotatepicright (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return

        self.image = self.image.rotate (-90, expand=True)
        # self.rotated = self.rotated ^ 1
        self.showimage ()

    def firstpic (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # Go to the first image in the list
        self.curimgidx = 0
        self.curimage = self.loaded [self.curimgidx]
        self.image = Image.open (str(self.curimage))
        self.showimage ()
        self.photoindex.set( str (self.curimgidx + 1))
        if self.curimage not in self.selected:
            self.selectbutton ["text"] = "SELECT"
        else:
            self.selectbutton ["text"] = "UNSELECT"

    def lastpic (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # Go to the last image in the list
        self.curimgidx = self.loadedsize - 1
        self.curimage = self.loaded [self.curimgidx]
        self.image = Image.open (str(self.curimage))
        self.showimage ()
        self.photoindex.set( str (self.curimgidx + 1))
        if self.curimage not in self.selected:
            self.selectbutton ["text"] = "SELECT"
        else:
            self.selectbutton ["text"] = "UNSELECT"

    def previouspic (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # Check for valid bounds of image list.
        if (self.curimgidx - 1 >= 0):
            self.curimage = self.loaded [self.curimgidx - 1]
            self.curimgidx = self.curimgidx - 1
            self.image = Image.open (str(self.curimage))
            self.showimage ()
            self.photoindex.set( str (self.curimgidx + 1))
            if self.curimage not in self.selected:
                self.selectbutton ["text"] = "SELECT"
            else:
                self.selectbutton ["text"] = "UNSELECT"

        else:
            tkMessageBox.showwarning ("Warning", "No previous images")
        return

    def nextpic (self):
        self.rotated = 0
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # Check for valid bounds of image list.
        if (self.curimgidx + 1 < self.loadedsize):
            self.curimage = self.loaded [self.curimgidx + 1]
            self.curimgidx = self.curimgidx + 1
            self.image = Image.open (str(self.curimage))
            self.showimage ()
            self.photoindex.set( str (self.curimgidx + 1))
            if self.curimage not in self.selected:
                self.selectbutton ["text"] = "SELECT"
            else:
                self.selectbutton ["text"] = "UNSELECT"

        else:
            tkMessageBox.showwarning ("Warning", "End of dir reached")

    # Get the index of the picture to be shown
    # Check if the image is there within bound
    def get (self, event):
        if not self.loaded:
            tkMessageBox.showwarning ("Warning", "Load the directory using LOAD button before calling GO TO")
        else:
            gotoindex = event.widget.get()
            #print gotoindex
            if gotoindex.isdigit() :
                index = int (gotoindex) - 1
                #print int(gotoindex)
                if ((index >= 0) and (index < self.loadedsize)):
                    self.curimage = self.loaded [index]
                    self.curimgidx = index
                    self.image = Image.open (str (self.curimage))
                    self.showimage()
                    self.photoindex.set (gotoindex)
                    if self.curimage not in self.selected:
                        self.selectbutton ["text"] = "SELECT"
                    else:
                        self.selectbutton ["text"] = "UNSELECT"
                else:
                    tkMessageBox.showerror("Error", "Invalid Entry!")
            else:
                tkMessageBox.showerror("Error", "Invalid Entry!")


    def loadpic (self):

        self.file_path_str = tkFileDialog.askdirectory (title='Choose image dir')
        if not self.file_path_str:
            tkMessageBox.showerror ("Error", "Choose valid dir")
            return

        self.loaded = [os.path.join (self.file_path_str, f) for f in os.listdir (self.file_path_str) if (f.lower().endswith ('gif') or
                    f.lower().endswith ('bmp') or f.lower().endswith ('jpg') or
                    f.lower().endswith ('jpeg')) ]
        self.loadedsize = len (self.loaded)
        self.curimgidx = 0
        if self.loadedsize == 0:
            tkMessageBox.showwarning ("Warning", "Empty dir; no images")
        else:
            self.textstring.set ("/" + str (self.loadedsize));
            self.photoindex.set(str(self.curimgidx + 1))
            self.curimage = self.loaded [self.curimgidx]
            self.image = Image.open (str (self.curimage))
            self.showimage ()
            tkMessageBox.showinfo ("Info", "Loaded %d images!" % self.loadedsize)


root = Tk()
root.wm_title ("Photo Manager")
app = App (root)

root.mainloop()
