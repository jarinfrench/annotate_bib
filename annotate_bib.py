#! /usr/bin/env python

from __future__ import print_function
from Tkinter import *
from tkMessageBox import *
import tkFileDialog
import os
import re


class App(object):
    def __init__(self, master):
        self.fields = ['Author(s)', 'Title', 'Journal', 'Year', 'Volume', 'Issue', 'Pages']
        self.data = {"AUTHOR": None, "TITLE": None, "JOURNAL": None, "YEAR": None,
            "VOLUME": None, "ISSUE": None, "PAGES": None, "SUMMARY": None,
            "CRITIQUE": None, "RELEVANCE": None}
        self.textFields = ['Summary', 'Critique', 'Relevance']
        self.myFileTypes = [("Annotated bibliography files", "*.anbib"), ("Text documents", "*.txt"), ("Bibliography files", "*.bib"), ("All file types", "*.*")]
        self.entries = []
        frame = Frame(master)
        frame.pack()

        menu = Menu(root)
        root.config(menu=menu)
        filemenu = Menu(menu)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="New", command = self.openNew)
        filemenu.add_command(label="Open", command = self.openFile)
        filemenu.add_command(label = "Save", command = self.saveFile)
        filemenu.add_command(label="Export Bibliography", command = self.exportBib)
        filemenu.add_separator()
        filemenu.add_command(label="Quit", command = root.quit)

        helpmenu = Menu(menu)
        menu.add_cascade(label = "Help", menu = helpmenu)
        helpmenu.add_command(label = "About...", command = self.askAbout)

    def openNew(self):
        for field in self.fields:
            row = Frame(root)
            lab = Label(row, width = 15, text = field, anchor = 'w')
            ent = Entry(row)
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            self.entries.append((field,ent))

        textEntries = Frame(root)
        for field in self.textFields:
            row = Frame(textEntries)
            s = Scrollbar(row)
            t = Text(row, height = 10, width = 80)
            row.pack(side=TOP, fill=X, padx = 5, pady = 40, expand = 1)
            lab = Label(row, width = 15, text = field)
            lab.pack(side=TOP)
            s.pack(side=RIGHT, fill=Y)
            t.pack(side=RIGHT, fill=BOTH, expand=1)
            s.config(command=t.yview)
            t.config(yscrollcommand=s.set)
        textEntries.pack(side=TOP, fill=X, padx=5, pady = 5, expand = 1)

    def openFile(self):
        self.filename = tkFileDialog.askopenfilename(initialdir = "~",
                        title = "Select file", filetypes = self.myFileTypes)
        text = self.readInFile()
        self.parseFile(text)
        #print(self.filename)

    def readInFile(self):
        if self.filename != '':
            text = []
            with open(self.filename, "r") as fopen:
                for line in fopen:
                    text.append(line)
            fopen.close()
        return text

    def parseFile(self, text):
        def parseAnbib(text):
            field_strings = ["AUTHOR", "TITLE", "JOURNAL", "YEAR", "VOLUME", "ISSUE", "PAGES", "SUMMARY", "CRITIQUE", "RELEVANCE"]
            data = []
            j = 0
            for i in range(len(text)):
                if (text[i].startswith("{")):
                    data.append(re.sub('[{}]', '', text[i]))
                    i = i + 1
                    while i < len(text) and not (text[i].startswith("{")):
                        data[j] = data[j] + re.sub('[}]', '', text[i])
                        i = i + 1
                    j = j + 1
            for i in range(len(data)):
                sub_data = data[i].split('; ')
                if sub_data[0] in field_strings:
                    self.data[sub_data[0]] = sub_data[1].replace("\n", '')
                    print("Found data %s in line %d"%(field_strings[field_strings.index(sub_data[0])], i))
                    print(sub_data[0], self.data[sub_data[0]])


        file_ext = os.path.splitext(self.filename)[1]
        if (file_ext == ".anbib"):
            print("Reading an Annotated Bibliography file.")
            parseAnbib(text)
        elif(file_ext == ".txt"):
            print("Reading a text file.")
            #parseTxt(text)
        elif(file_ext == ".bib"):
            print("Reading a LaTeX Bibliography file.")
            #parseBib(text)
        else:
            print("Reading an unknown file format")
            #parseOther(text)


    def saveFile(self):
        save_dialog = tkFileDialog.Save(root, initialdir = "~",
                        title = "Select save destination", filetypes = self.myFileTypes)
        statusbar = label(root, text = "", bd = 1, relief = SUNKEN, anchor = W)
        statusbar.pack(side = BOTTOM, fill = X)
        statusbar.config(text = save_dialog.show())
        print("Saving file")

    def exportBib(self):
        msg = "Bibliography exported to annotated_bib.bib"
        export_win = Toplevel()
        export_win.geometry('300x200')
        export_win.wm_title("")

        export_label = Label(export_win, text = msg)
        export_label.pack(side = TOP, fill = X, padx = 5, pady = 5)

        quit_button = Button(export_win, text="Ok", command = export_win.destroy)
        quit_button.pack(side = TOP)

    def askAbout(self):
        msg = "This is the About menu item"
        about_win = Toplevel()
        about_win.geometry('300x200')
        about_win.wm_title("About Annotated Bibliography")

        about_label = Label(about_win, text = msg)
        about_label.pack(side = TOP, fill = X, padx = 5, pady = 5)

        quit_button = Button(about_win, text="Ok", command = about_win.destroy)
        quit_button.pack(side = TOP)

    def fetch(self):
        for entry in self.entries:
            field = entry[0]
            text = entry[1].get()
            print('%s: "%s"' % (field, text))

if __name__ == "__main__":
    root = Tk()
    root.title("Annotated Bibliography")
    root.geometry('2000x1000')
    app = App(root)
    root.mainloop()
