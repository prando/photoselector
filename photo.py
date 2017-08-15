from Tkinter import *
import tkMessageBox
import tkFileDialog
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

        # Image load path
        self.file_path_str = []
        # Selected image list file path
        self.out_file_path_str = []

        # Setup a frame (child of master) to display buttons
        self.frame = Frame (master)
        # Show frame.
        self.frame.pack()

        # Setup a frame (child of Frame) to display image
        self.imframe = Frame (self.frame)
        # Show frame.
        self.imframe.pack(side=BOTTOM)

        # Setup buttons with actions triggering command=$$$ function.
        self.loadbutton = Button (self.frame, text="LOAD", command=self.loadpic)
        self.loadbutton.pack(side=LEFT)

        self.firstbutton = Button (self.frame, text="FIRST", command=self.firstpic)
        self.firstbutton.pack(side=LEFT)

        self.lastbutton = Button (self.frame, text="LAST", command=self.lastpic)
        self.lastbutton.pack(side=LEFT)

        self.quitbutton = Button (self.frame, text="QUIT", command=self.quitprog)
        self.quitbutton.pack(side=LEFT)

        self.selectbutton = Button (self.frame, text="SELECT", command=self.selectpic)
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
        self.txtlabel = Label (self.imframe, textvar=self.textstring)
        self.txtlabel.pack(side=LEFT)

    # Quit button action.
    def quitprog (self):
        # If selected list is not empty, prompt user for location to save list of selected images & append to it.
        if self.selected:
            self.out_file_path_str = tkFileDialog.askdirectory (title='Choose target dir to store selected files')
            if not self.out_file_path_str:
                tkMessageBox.showerror ("Error", "Choose valid dir")
                return
            self.out_file_path_str = os.path.join (self.out_file_path_str, 'selected_photos.txt')
            with open (self.out_file_path_str, "a") as f:
                for n in self.selected:
                    f.write (n+"\n")

        # Quit program.
        self.frame.quit ()

    # Select button action.
    def selectpic (self):
        # Handle error condition: No images loaded yet.
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # If selected, add to list if not previously added.
        if self.curimage not in self.selected:
            self.selected.append(self.curimage)
        else:
            tkMessageBox.showwarning("Warning", "Already selected!")

    def showimage (self):

        #width, height = self.image.size
        #ratio = height/float (width)
        #width = 800
        #height = int (width * ratio)

        #self.image = self.image.resize ((width, height), Image.ANTIALIAS)
        self.image.thumbnail ((768, 512), Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(self.image)
        self.imlabel = Label (self.imframe, image=photo, height=512, width=768)
        self.imlabel.image = photo
        self.imlabel.pack(side=BOTTOM)
        if self.oldimlabel is not None:
            self.oldimlabel.destroy()
        self.oldimlabel = self.imlabel

    def rotatepicleft (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return

        self.image = self.image.rotate(90, expand=True)
        self.showimage ()

    def rotatepicright (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return

        self.image = self.image.rotate(-90, expand=True)
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
        self.textstring.set( str (self.curimgidx + 1) + "/" + str (self.loadedsize))

    def lastpic (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # Go to the last image in the list
        self.curimgidx = self.loadedsize - 1
        self.curimage = self.loaded [self.curimgidx]
        self.image = Image.open (str(self.curimage))
        self.showimage ()
        self.textstring.set( str (self.curimgidx + 1) + "/" + str (self.loadedsize))

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
            self.textstring.set( str (self.curimgidx + 1) + "/" + str (self.loadedsize))
        else:
            tkMessageBox.showwarning ("Warning", "No previous images")
        return

    def nextpic (self):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return

        if (self.curimgidx + 1 < self.loadedsize):
            self.curimage = self.loaded [self.curimgidx + 1]
            self.curimgidx = self.curimgidx + 1
            self.image = Image.open (str(self.curimage))
            self.textstring.set( str (self.curimgidx + 1) + "/" + str (self.loadedsize))
            self.showimage ()
        else:
            tkMessageBox.showwarning ("Warning", "End of dir reached")

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
        if self.loadedsize is 0:
            tkMessageBox.showwarning ("Warning", "Empty dir; no images")
        else:
            self.curimage = self.loaded [self.curimgidx]
            self.image = Image.open (str (self.curimage))
            self.textstring.set (str (self.curimgidx + 1) + "/" + str (self.loadedsize))
            self.showimage ()
            tkMessageBox.showinfo ("Info", "Loaded %d images!" % self.loadedsize)


root = Tk()
root.wm_title ("Photo Manager")
app = App (root)

root.mainloop()
