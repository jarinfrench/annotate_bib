#! /usr/bin/env python

from __future__ import print_function
import sys
if sys.version_info[0] == 2:
    from Tkinter import *
    #from tkMessageBox import *
else:
    from tkinter import *
    from tkinter import messagebox
    from tkinter import filedialog
import os
import re
import collections


class App(object):
    def __init__(self, master):
        self.fields = ['Author(s)', 'Title', 'Journal', 'Year', 
                       'Volume', 'Issue', 'Pages']
        self.data_keys = ["AUTHOR", "TITLE", "JOURNAL", "YEAR", "VOLUME", 
                          "ISSUE", "PAGES", "SUMMARY", "CRITIQUE", "RELEVANCE"]
        self.data = collections.OrderedDict({"AUTHOR": StringVar(), "TITLE": StringVar(), 
                     "JOURNAL": StringVar(), "YEAR": StringVar(),
                     "VOLUME": StringVar(), "ISSUE": StringVar(), 
                     "PAGES": StringVar(), "SUMMARY": StringVar(),
                     "CRITIQUE": StringVar(), "RELEVANCE": StringVar()})
        self.textFields = ['Summary', 'Critique', 'Relevance']
        self.myFileTypes = [("Annotated bibliography files", "*.anbib"), 
                            ("Text documents", "*.txt"), 
                            ("Bibliography files", "*.bib"), 
                            ("All file types", "*.*")]
        self.windowOpen = False
        self.entries = {}
        self.textEntries = {}
        
        # Set keybindings
        master.bind("<Control-n>", self.openNew)
        master.bind("<Control-s>", self.saveFile)
        master.bind("<Control-o>", self.openFile)
        master.bind("<Control-w>", self.on_exit)
        root.protocol("WM_DELETE_WINDOW", self.on_exit) # exit protocol
        #self.frame = Frame(master)
        #self.frame.place(relwidth = 0.5, relheight = 0.5, )

        self.menu = Menu(root)
        root.config(menu=self.menu)
        self.menu.filemenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.menu.filemenu)
        self.menu.filemenu.add_command(label="New", command = self.openNew)
        self.menu.filemenu.add_command(label="Open", command = self.openFile)
        self.menu.filemenu.add_command(label = "Save", command = self.saveFile, 
                                       state = "disabled")
        self.menu.filemenu.add_command(label = "Save As", 
                                       command = self.saveFile, 
                                       state = "disabled")
        self.menu.filemenu.add_command(label="Export Bibliography", 
                                       command = self.exportBib)
        self.menu.filemenu.add_separator()
        self.menu.filemenu.add_command(label="Quit", command = root.destroy)

        self.menu.helpmenu = Menu(self.menu)
        self.menu.add_cascade(label = "Help", menu = self.menu.helpmenu)
        self.menu.helpmenu.add_command(label = "About...", command = self.askAbout)
    
    def on_exit(self, event = None):
        if messagebox.askyesno("Exit", "Do you want to quit the application?"):
            root.destroy()
            root.quit()

    def openNew(self, event = None):
        for field in self.fields:
            row = Frame(root)
            lab = Label(row, width = 15, text = field, anchor = 'w')
            ent = Entry(row)
            row.pack(side=TOP, expand = YES, fill=X, padx=50)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand = YES, fill=X)
            lab.config(font = "Helvetica 16")
            ent.config(font = "Helvetica 10")
            self.entries[field] = ent

        textEntries = Frame(root)
        for field in self.textFields:
            row = Frame(textEntries)
            s = Scrollbar(row)
            t = Text(row, height = 5, width = 80, wrap = WORD)
            row.pack(side=TOP, expand = YES, fill=X, padx = 5)
            lab = Label(row, width = 15, text = field, font = "Helvetica 16")
            lab.pack(side=TOP, expand = NO)
            s.pack(side=RIGHT, fill=Y)
            t.pack(side=RIGHT, expand = YES, fill=BOTH)
            s.config(command=t.yview)
            t.config(yscrollcommand=s.set, font = "Helvetica 10")
            self.textEntries[field] = t
        textEntries.pack(side=TOP, fill=X, padx=5, pady = 5, expand = 1)
        self.menu.filemenu.entryconfig("Save", state = "normal")
        self.menu.filemenu.entryconfig("Save As", state = "normal")


    def openFile(self, event = None):
        self.filename = filedialog.askopenfilename(initialdir = "~",
                        title = "Select file", filetypes = self.myFileTypes)
        if not self.windowOpen:
            self.openNew()
            self.windowOpen = True
        if self.filename is not '':
            for key in self.textEntries.keys():
                self.textEntries[key].delete(1.0, END)
            for key in self.entries.keys():
                self.entries[key].delete(0, END)
            text = self.readInFile()
            self.parseFile(text)

    def readInFile(self):
        if self.filename != '':
            text = []
            with open(self.filename, "r") as fopen:
                for line in fopen:
                    text.append(line)
            fopen.close()
        return text

    def parseFile(self, text):
        field_strings = ["AUTHOR", "TITLE", "JOURNAL", "YEAR", 
                         "VOLUME", "ISSUE", "PAGES", "SUMMARY", 
                         "CRITIQUE", "RELEVANCE"]
        def populateFields(dataset):
            self.entries["Author(s)"].insert(END, dataset["AUTHOR"].get())
            self.entries["Title"].insert(END, dataset["TITLE"].get())
            self.entries["Journal"].insert(END, dataset["JOURNAL"].get())
            self.entries["Year"].insert(END, dataset["YEAR"].get())
            self.entries["Volume"].insert(END, dataset["VOLUME"].get())
            self.entries["Issue"].insert(END, dataset["ISSUE"].get())
            self.entries["Pages"].insert(END, dataset["PAGES"].get())
            self.textEntries["Summary"].insert(END, dataset["SUMMARY"].get())
            self.textEntries["Critique"].insert(END, dataset["CRITIQUE"].get())
            self.textEntries["Relevance"].insert(END, dataset["RELEVANCE"].get())
            
        def parseAnbib(text):
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
                    self.data[sub_data[0]].set(sub_data[1].replace("\n", ' '))
            populateFields(self.data)
        
        def parseTxt(text):
            data = []
            j = 0
            for line in text: # for each line in text
                line_array = line.split()
                if len(line_array) == 0:
                    continue
                elif re.sub(':', '', line_array[0]) in field_strings:
                    data.append([re.sub(':', '', line_array[0]), ' '.join(line_array[1:])])
                    j = j + 1
                else:
                    data[j-1][1] = data[j-1][1] + line.replace("\n", ' ')
            #print(data)
            for data_key, data_val in data:
                self.data[data_key].set(data_val)
            populateFields(self.data)
        
        def parseBib(text):
            # Note that a bib file may contain multiple entries!  In this case,
            # should I open up a separate file for each of them?  Or should I
            # prompt the user for which data entry to edit?
            # For now, here is a one-entry bib file.            
            text = re.sub("\n",' ',' '.join(text))
            bib_labels = re.findall(r"@(.*?){\s*?(.*?),", text)
            data = [self.data] * len(bib_labels)
            self.menu.bibtexMenu = Menu(self.menu)
            self.menu.add_cascade(label = "BibTex Entries", menu = self.menu.bibtexMenu)
            
            read_error = '''Error reading file %s.
Make sure the first line of the file is specified in .bib format! (@type{...'''%self.filename
            regexs = [r"(?i)author\s*?=\s*?([{\"].*?[}\"])",
                      r"(?i)title\s*?=\s*?([{\"].*?[}\"])",
                      r"(?i)journal\s*?=\s*?([{\"].*?[}\"])",
                      r"(?i)year\s*?=\s*?([{\"].*?[}\"])",
                      r"(?i)volume\s*?=\s*?([{\"].*?[}\"])",
                      r"(?i)number\s*?=\s*?([{\"].*?[}\"])",
                      r"(?i)pages\s*?=\s*?([{\"].*?[}\"])",
                      r"(?i)summary(:|(\s*?-))\s*?(.*?(?=(critique|relevance|@|$)))",
                      r"(?i)critique(:|(\s*?-))\s*?(.*?(?=(summary|relevance|@|$)))",
                      r"(?i)relevance(:|(\s*?-))\s*?(.*?(?=(critique|summary|@|$)))"]
            if not text.startswith("@"):
                messagebox.showerror("Read Error", read_error)
                # read each line until we either a) come to two } symbols next
                # to each other, b) come to a "} set of symbols, or c) come to
                # a line that starts with a }
            for i in range(len(regexs)):
                result = re.findall(regexs[i], text)
                print(result)
                if result:
                    for j in range(len(result)):
                        if i < 7:
                            # Make sure the brackets or quotation marks match!
                            if (result[j].group(1).startswith("{") and 
                            result[j].group(1).endswith("}")) or \
                            (result[j].group(1).startswith("\"") and 
                            result[j].group(1).endswith("\"")):
                                data[j][self.data_keys[i]].set(result[j].group(1)[1:-1])
                        else: # summary, critique, and relevance
                            data[j][self.data_keys[i]].set((result[j].group(3)).strip())
                    #print (self.data[self.data_keys[i]].get())
            for i in range(len(bib_labels)):
                self.menu.bibtexMenu.add_command(label = bib_labels[i][1],
                                                 command = (lambda: populateFields(data[i])))
                


        file_ext = os.path.splitext(self.filename)[1]
        if (file_ext == ".anbib"):
            parseAnbib(text)
        elif(file_ext == ".txt"):
            parseTxt(text)
        elif(file_ext == ".bib"):
            print("Reading a LaTeX Bibliography file.")
            parseBib(text)
        else:
            print("Reading an unknown file format")
            #parseOther(text)

    def saveFile(self, event = None):
        save_dialog = filedialog.asksaveasfilename(root, initialdir = "~",
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
    #m = root.maxsize()
    #print(m)
    #root.geometry('{}x{}+0+0'.format(*m))
    root.wm_state("zoomed")
    #screen_width = root.winfo_screenwidth()
    #screen_height = root.winfo_screenheight()
    #root.geometry('%sx%s'%(screen_width, screen_height))
    app = App(root)
    root.mainloop()
