from Tkinter import *
import tkMessageBox
import tkFileDialog
import os

from PIL import Image, ImageTk

class App:
    def __init__(self, master):

        self.curimage = None
        self.curimgidx = 0

        self.loaded = []
        self.selected = []
        self.rejected = []
        self.tentative = []

        self.file_path_str = []

        self.frame = Frame (master)
        self.frame.pack()

        self.imframe = Frame (self.frame)
        self.imframe.pack(side=BOTTOM)

        self.loadbutton = Button (self.frame, text="LOAD", command=self.loadpic)
        self.loadbutton.pack(side=LEFT)

        self.quitbutton = Button (self.frame, text="QUIT", command=self.quitprog)
        self.quitbutton.pack(side=LEFT)

        self.selectbutton = Button (self.frame, text="SELECT", command=self.selectpic)
        self.selectbutton.pack(side=LEFT)

        self.nextbutton = Button (self.frame, text="NEXT", command=self.nextpic)
        self.nextbutton.pack(side=LEFT)

        self.previousbutton = Button (self.frame, text="PREVIOUS", command=self.previouspic)
        self.previousbutton.pack(side=LEFT)

        self.rotatebutton = Button (self.frame, text="ROTATE", command=self.rotatepic)
        self.rotatebutton.pack(side=LEFT)

        self.oldlabel = None

    def quitprog (self):
        for f in self.selected:
            print f
        self.frame.quit()

    def selectpic (self):

        if (self.curimage is None):
            tkMessageBox.showinfo("Error", "Load images first!")
            return

        if self.curimage not in self.selected:
            self.selected.append(self.curimage)
        else:
            tkMessageBox.showinfo("Warning", "Already selected!")

    def showimage (self):

        width, height = self.image.size
        ratio = height/float (width)
        targetwidth = 500
        targetheight = int (targetwidth * ratio)

        self.image = self.image.resize((targetwidth, targetheight), Image.ANTIALIAS)

        photo = ImageTk.PhotoImage(self.image)
        self.label = Label (self.imframe, image=photo)
        self.label.image = photo
        self.label.pack(side=BOTTOM)
        if self.oldlabel is not None:
            self.oldlabel.destroy()
        self.oldlabel = self.label

    def rotatepic(self):
        if (self.curimage is None):
            tkMessageBox.showinfo("Error", "Load images first!")
            return

        self.image = self.image.rotate(90)
        self.showimage ()

    def previouspic (self):
        if (self.curimage is None):
            tkMessageBox.showinfo("Error", "Load images first!")
            return

        if (self.curimgidx - 1 >= 0):
            self.curimage = self.loaded [self.curimgidx - 1]
            self.curimgidx = self.curimgidx - 1
            self.image = Image.open (str(self.curimage))
            self.showimage ()
        else:
            tkMessageBox.showinfo("Warning", "No previous images")
        return

    def nextpic (self):
        if (self.curimage is None):
            tkMessageBox.showinfo("Error", "Load images first!")
            return

        if (self.curimgidx + 1 < self.loadedsize):
            self.curimage = self.loaded [self.curimgidx + 1]
            self.curimgidx = self.curimgidx + 1
            self.image = Image.open (str(self.curimage))
            self.showimage ()
        else:
            tkMessageBox.showinfo("Warning", "End of dir reached")

    def loadpic (self):

        self.file_path_str = tkFileDialog.askdirectory()
        self.loaded = [os.path.join(self.file_path_str,f) for f in os.listdir (self.file_path_str) if (f.lower().endswith('jpg') or f.lower().endswith ('jpeg')) ]
        self.loadedsize = len (self.loaded)
        self.curimgidx = 0
        if self.loadedsize is 0:
            tkMessageBox.showinfo("Warning", "Empty dir; no images")
        else:
            self.curimage = self.loaded [self.curimgidx]
            self.image = Image.open (str(self.curimage))
            self.showimage ()
            tkMessageBox.showinfo("Warning", "Dir Loaded with %d images!" % self.loadedsize)


root = Tk()
app = App (root)

root.mainloop()


