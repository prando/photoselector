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

        # List of all button instances in GUI
        self.buttonlist = []
        
        # Setup buttons with actions triggering command=$$$ function.
        self.loadpicbutton = self.createbuttons (self.frame, "LOAD", lambda: self.loadpic (handler=self.buttonHandler), LEFT, 0, state="normal")
        self.selectbutton = self.createbuttons (self.frame, "SELECT", lambda: self.selectpic (handler=None) , LEFT, 10, state="disabled")
        self.firstpicbutton = self.createbuttons (self.frame, "FIRST", lambda: self.firstpic (handler=self.buttonHandler), LEFT, 0, state="disabled")
        self.lastpicbutton = self.createbuttons (self.frame, "LAST", lambda: self.lastpic (handler=self.buttonHandler), LEFT, 0, state="disabled")
        self.quitprogbutton = self.createbuttons (self.frame, "QUIT",  lambda: self.quitprog (handler=self.newToplevel), RIGHT, 0, state="disabled")
        self.nextpicbutton = self.createbuttons (self.frame, "NEXT", lambda: self.nextpic (handler=self.buttonHandler), LEFT, 0, state="disabled")
        self.previouspicbutton = self.createbuttons (self.frame, "PREVIOUS", lambda: self.previouspic (handler=self.buttonHandler), LEFT, 0, state="disabled")
        self.rotatepicleftbutton = self.createbuttons (self.frame, "ROTATE LEFT", lambda: self.rotatepicleft (handler=None), RIGHT, 0, state="disabled")
        self.rotatepicrightbutton = self.createbuttons (self.frame, "ROTATE RIGHT", lambda: self.rotatepicright (handler=None), RIGHT, 0, state="disabled")

        # Set up a label with entry to take input for Go-to a particular photo
        self.gotolabel = Label (self.txtboxframe, textvar= self.textstring)
        self.gotolabel.pack (side=RIGHT)
        self.txtbox = Entry (self.txtboxframe, textvariable=self.photoindex, bd=1, width=4, justify=RIGHT)
        self.txtbox.bind ('<Return>', lambda event: self.get (event, handler=self.buttonHandler))
        self.txtbox.pack (side=LEFT)

    def createbuttons (self, master, buttonstr, command, side, width, state="normal"):
        button = Button (master, text=buttonstr, command=command, width=width, state=state)
        button.pack (side=side)
        self.buttonlist.append (button)
        return button

    def disablePreviousButton (self):
      self.previouspicbutton ["state"] = "disabled"
      return 
    
    def enablePreviousButton (self):
      self.previouspicbutton ["state"] = "normal"
      return 
    
    def disableNextButton (self):
      self.nextpicbutton ["state"] = "disabled"
      return 
    
    def enableNextButton (self):
      self.nextpicbutton ["state"] = "normal"
      return 
    
    def buttonHandler (self):
        if (self.curimgidx == 0):
          self.disablePreviousButton ()
        else:
          self.enablePreviousButton ()
        if (self.curimgidx == self.loadedsize-1):
          self.disableNextButton ()
        else:
          self.enableNextButton ()
    
    def newToplevel (self):
      childwindow = Toplevel ()
      label = Label (childwindow, text="HELLO")
      label.pack (side=TOP)

    # Quit button action.
    def quitprog (self, handler=None):

        if (handler is not None):
          handler()
 
        # If selected list is not empty, prompt user for location to save list of selected images & append to it.
        if self.selected:
            self.out_file_path_str = tkFileDialog.askdirectory (title='Choose target dir to store selected files')
            if not self.out_file_path_str:
                tkMessageBox.showerror ("Error", "Choose valid dir")
                return
            self.out_file_path_str = os.path.join (self.out_file_path_str, 'selected_photos.txt')
            with open (self.out_file_path_str, "a") as f:
                for n in self.selected:
                    f.write (self.loaded [n]+"\n")

        # Quit program.
        self.frame.quit ()

    # Select button action.
    def selectpic (self, handler=None):
        # Handle error condition: No images loaded yet.
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # If selected, add to list if not previously added.
        if self.selectbutton ["text"] == "SELECT":
            if self.curimgidx not in self.selected:
                self.selected.append (self.curimgidx)
                self.selectbutton ["text"] = "UNSELECT"
            else:
                tkMessageBox.showwarning ("Warning", "Already selected!")
        else:
            self.selected.remove (self.curimgidx)
            self.selectbutton ["text"] = "SELECT"

        if (handler is not None):
          handler()

    def showimage (self):

        # if self.rotated:
        #     self.image.thumbnail ((648, 648), Image.ANTIALIAS)
        # else:
        #     self.image.thumbnail ((648, 648), Image.ANTIALIAS)
        self.image.thumbnail ((648, 648), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage (self.image)
        self.imlabel = Label (self.imframe, image=photo, height=648, width=648)
        self.imlabel.image = photo
        self.imlabel.pack (side=BOTTOM)
        if self.oldimlabel is not None:
            self.oldimlabel.destroy ()
        # Save a reference to image label (enables destroying to repaint)
        self.oldimlabel = self.imlabel

    def rotatepicleft (self, handler=None):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return

        self.image = self.image.rotate (90, expand=True)
        self.showimage ()
        if (handler is not None):
          handler()

    def rotatepicright (self, handler=None):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return

        self.image = self.image.rotate (-90, expand=True)
        self.showimage ()
        if (handler is not None):
          handler()


    def firstpic (self, handler=None):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # Go to the first image in the list
        self.curimgidx = 0
        self.curimage = self.loaded [self.curimgidx]
        self.image = Image.open (str(self.curimage))
        self.showimage ()
        self.photoindex.set (str (self.curimgidx + 1))
        if self.curimgidx not in self.selected:
            self.selectbutton ["text"] = "SELECT"
        else:
            self.selectbutton ["text"] = "UNSELECT"
        if (handler is not None):
          handler()

    def lastpic (self, handler=None):
        if (self.curimage is None):
            tkMessageBox.showerror ("Error", "Load images first!")
            return
        # Go to the last image in the list
        self.curimgidx = self.loadedsize - 1
        self.curimage = self.loaded [self.curimgidx]
        self.image = Image.open (str(self.curimage))
        self.showimage ()
        self.photoindex.set( str (self.curimgidx + 1))
        if self.curimgidx not in self.selected:
            self.selectbutton ["text"] = "SELECT"
        else:
            self.selectbutton ["text"] = "UNSELECT"
        if (handler is not None):
          handler()

    def previouspic (self, handler=None):
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
            if self.curimgidx not in self.selected:
                self.selectbutton ["text"] = "SELECT"
            else:
                self.selectbutton ["text"] = "UNSELECT"

        if (handler is not None):
          handler()
        return

    def nextpic (self, handler=None):
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
            if self.curimgidx not in self.selected:
                self.selectbutton ["text"] = "SELECT"
            else:
                self.selectbutton ["text"] = "UNSELECT"
       
        if (handler is not None):
          handler()
    # Get the index of the picture to be shown
    # Check if the image is there within bound
    def get (self, event, handler=None):
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
                    if self.curimgidx not in self.selected:
                        self.selectbutton ["text"] = "SELECT"
                    else:
                        self.selectbutton ["text"] = "UNSELECT"
                    if handler is not None:
                      handler()
                else:
                    tkMessageBox.showerror("Error", "Invalid Entry!")
            else:
                tkMessageBox.showerror("Error", "Invalid Entry!")


    def loadpic (self, handler=None):

        self.file_path_str = tkFileDialog.askdirectory (title='Select images directory')
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
            return 
        else:
            self.textstring.set ("/" + str (self.loadedsize));
            self.photoindex.set(str(self.curimgidx + 1))
            self.curimage = self.loaded [self.curimgidx]
            self.image = Image.open (str (self.curimage))
            self.showimage ()
            # tkMessageBox.showinfo ("Info", "Loaded %d images!" % self.loadedsize)

        for button in self.buttonlist:
          button["state"] = "normal" 

        if (handler is not None):
          handler()

root = Tk()
root.wm_title ("Photo Manager")
app = App (root)

root.mainloop()
