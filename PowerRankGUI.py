from Tkinter import *
import ttk
import tkFileDialog
import tkMessageBox
import PowerRankWorker
import threading
import re
import os
import Queue
import ScrolledText

class PowerRankGUI(Frame):
    def __init__(self, master=None):
        master.minsize(width=500, height=250)
        Frame.__init__(self, master)
        self.grid()
        self.inputFileName = ""#used to store the file
        self.inputFileDisplay = StringVar()#used to show the file name
        self.runButton = None #used to store the button
        self.waitingForUserInput = False
        
        self.prWorker = None
        
        self.createWidgets()

    def createWidgets(self):
        self.browse = Button(self, text="Browse", command=self.get_file)
        self.browse.grid(row=2, column=0, sticky = "NWSE")
        
        #file name display
        self.fileNameDisplay = Label(self, textvariable=self.inputFileDisplay).grid(row=2, column=1)
        
        #Go button
        self.runButton = Button(self, text="Go", width=10, command=lambda: self.spawnPRWorker(self.inputFileName))
        self.runButton.grid(row=3, column=0, sticky="NWSE")
        
        #text box
        self.textBox = ScrolledText.ScrolledText(self, height=20, width= 30)
        self.textBox.grid(row=4, column=1, rowspan=10, sticky="NS")

    
    def spawnPRWorker(self, filename):
        if self.inputFileName == '':
            self.textBox.insert(END, "Please select an input file with all of the Challonge URLs.")
        else:
            self.runButton.config(state="disabled")
            if self.waitingForUserInput is True:
                self.prWorker.userInputText = self.textBox.get(1.0, END)
                self.prWorker.userInputComplete = True
                while self.prWorker.finished is False:
                    pass
                tkMessageBox.showinfo("PR Calculator", "PR_ranks.txt has been created.")
            else:
                self.textBox.delete(1.0, END)
                self.progBar = ttk.Progressbar(self, orient='horizontal', mode='indeterminate', maximum=50)
                self.progBar.start(10);
                self.progBar.grid(row=3, column=1)
                
                self.prWorker = PowerRankWorker.PowerRankWorker(filename)
                self.prWorker.daemon = True
                self.prWorker.start()
                self.after(5000, self.createPlayerList);
            
        
    def createPlayerList(self):
        if self.prWorker.waiting is True:
            for name in sorted(self.prWorker.uniquePlayers.keys()):
                self.textBox.insert(END, name+" = \n")
            self.waitingForUserInput = True
            self.runButton.config(state="normal")
            self.progBar.grid_forget()
        else:
            self.after(3000, self.createPlayerList)
        
    def get_file(self):
        fileName = tkFileDialog.askopenfilename()
        self.inputFileName = os.path.normpath(fileName)
        #print self.inputFileName
        self.inputFileDisplay.set(re.sub(".*(/|\\\)(.*)$", r"\2", fileName))
    
        
        

    

root = Tk()
root.wm_title("Power Rankings Calculator")
app = PowerRankGUI(master=root)
app.mainloop()