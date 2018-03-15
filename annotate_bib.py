#! /usr/bin/env python3

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
import platform
import re
import copy
import textwrap

def is_empty(struct):
    if struct:
        return False
    else:
        return True

class App(object):
    def __init__(self, master):
        self.fields = ['Author(s)', 'Title', 'Journal', 'Year',
                       'Volume', 'Issue', 'Pages']
        self.data_keys = ["AUTHOR", "TITLE", "JOURNAL", "YEAR", "VOLUME",
                          "ISSUE", "PAGES", "SUMMARY", "CRITIQUE", "RELEVANCE"]
        self.data = {"AUTHOR": StringVar(), "TITLE": StringVar(),
                     "JOURNAL": StringVar(), "YEAR": StringVar(),
                     "VOLUME": StringVar(), "ISSUE": StringVar(),
                     "PAGES": StringVar(), "SUMMARY": StringVar(),
                     "CRITIQUE": StringVar(), "RELEVANCE": StringVar()}
        for key in self.data_keys:
            self.data[key].trace("w", self.toggleSaveState)
        self.textFields = ['Summary', 'Critique', 'Relevance']
        self.myFileTypes = [("Annotated bibliography files", "*.anbib"),
                            ("Text documents", "*.txt"),
                            ("Bibliography files", "*.bib"),
                            ("All file types", "*.*")]
        self.filename = ''
        self.windowOpen = False
        self.isSaved = True
        self.entries = {}
        self.textEntries = {}
        self.bib_labels = []

        # Set keybindings
        master.bind("<Control-n>", self.openNew)
        master.bind("<Control-s>", self.saveFile)
        master.bind("<Control-S>", self.saveFileAs)
        master.bind("<Control-o>", self.openFile)
        master.bind("<Control-w>", self.on_exit)
        master.bind("<Control-e>", self.exportBib)
        root.protocol("WM_DELETE_WINDOW", self.on_exit) # exit protocol

        self.menu = Menu(root)
        root.config(menu=self.menu)
        self.menu.filemenu = Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.menu.filemenu)
        self.menu.filemenu.add_command(label= "New", command = self.openNew, accelerator = "Ctrl+N")
        self.menu.filemenu.add_command(label= "Open", command = self.openFile, accelerator = "Ctrl+O")
        self.menu.filemenu.add_command(label = "Save", command = self.saveFile, accelerator = "Ctrl+S",
                                       state = "disabled")
        self.menu.filemenu.add_command(label = "Save As",
                                       command = self.saveFileAs, accelerator = "Ctrl+Shift+S",
                                       state = "disabled")
        self.menu.filemenu.add_command(label= "Export Bibliography",
                                       command = self.exportBib, accelerator = "Ctrl+E")
        self.menu.filemenu.add_separator()
        self.menu.filemenu.add_command(label= "Quit", command = root.destroy)

        self.menu.bibtexMenu = Menu(self.menu)
        self.menu.add_cascade(label = "BibTex Entries", menu = self.menu.bibtexMenu, state = "disabled")

        self.menu.helpmenu = Menu(self.menu)
        self.menu.add_cascade(label = "Help", menu = self.menu.helpmenu)
        self.menu.helpmenu.add_command(label = "About...", command = self.askAbout)

    def toggleSaveState(self, event = None):
        self.isSaved = False
        # NOTE: https://stackoverflow.com/questions/6548837/how-do-i-get-an-event-callback-when-a-tkinter-entry-widget-is-modified/6549535
        # provides some info on callbacks to change the save state of a file


    def on_exit(self, event = None):
        if not self.isSaved:
            if messagebox.askyesno("", "%s has changes, do you want to save them?"):
                self.saveFile()
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
            t.bind("<<Modified>>", self.toggleSaveState)
            self.textEntries[field] = t
        textEntries.pack(side=TOP, fill=X, padx=5, pady = 5, expand = 1)
        self.menu.filemenu.entryconfig("Save", state = "normal")
        self.menu.filemenu.entryconfig("Save As", state = "normal")

    def openFile(self, event = None):
        self.filename = filedialog.askopenfilename(initialdir = "~",
                        title = "Select file", filetypes = self.myFileTypes)

        if not is_empty(self.filename):
            if not self.windowOpen:
                self.openNew()
                self.windowOpen = True
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
            for key in self.textEntries.keys():
                self.textEntries[key].delete(1.0, END)
            for key in self.entries.keys():
                self.entries[key].delete(0, END)
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
            self.bib_labels = re.findall(r"@(.*?){\s*?(.*?),", text)
            data = []
            for i in range(len(self.bib_labels)):
                data.append({"AUTHOR": StringVar(), "TITLE": StringVar(),
                             "JOURNAL": StringVar(), "YEAR": StringVar(),
                             "VOLUME": StringVar(), "ISSUE": StringVar(),
                             "PAGES": StringVar(), "SUMMARY": StringVar(),
                             "CRITIQUE": StringVar(), "RELEVANCE": StringVar()})
                for key in self.data_keys:
                    data[i][key].trace("w", self.toggleSaveState)

            read_error = '''Error reading file %s.\nMake sure the first line of the file is specified in .bib format! (@type{...'''%self.filename
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
                return
            for i in range(len(regexs)):
                result = re.findall(regexs[i], text)
                if result:
                    for j in range(len(result)):
                        if i < 7:
                            # Make sure the brackets or quotation marks match!
                            if (result[j].startswith("{") and
                            result[j].endswith("}")) or \
                            (result[j].startswith("\"") and
                            result[j].endswith("\"")):
                                data[j][self.data_keys[i]].set(result[j][1:-1])
                        else: # summary, critique, and relevance
                            data[j][self.data_keys[i]].set(result[j][2].strip())
            for i in range(len(self.bib_labels)):
                self.menu.bibtexMenu.add_command(label = self.bib_labels[i][1],
                                                 command = (lambda i=i: populateFields(data[i])))

            populateFields(data[0])
            self.data = data

        file_ext = os.path.splitext(self.filename)[1]
        if (file_ext == ".anbib"):
            self.menu.entryconfig("BibTex Entries", state = "disabled")
            parseAnbib(text)
        elif(file_ext == ".txt"):
            self.menu.entryconfig("BibTex Entries", state = "disabled")
            parseTxt(text)
        elif(file_ext == ".bib"):
            self.menu.entryconfig("BibTex Entries", state = "normal")
            parseBib(text)
        else:
            print("Reading an unknown file format")
            #parseOther(text)

    def saveFile(self, event = None):
        if self.menu.filemenu.entrycget("Save", "state") == "disabled":
            return

        if is_empty(self.filename):
            self.saveFileAs()
        else:
            ext = os.path.splitext(self.filename)[1]

            with open(self.filename, 'w') as fout:
                if ext == ".anbib":
                    self.saveAsAnBib(fout)
                elif ext == ".txt":
                    self.saveAsTxt(fout)
                elif ext == ".bib":
                    self.saveAsBib(fout)
                else:
                    messagebox.showerror("Could Not Save File!", "Could not save file %s"%self.filename)
        self.isSaved = True

    def saveFileAs(self, event = None):
        if (self.menu.filemenu.entrycget("Save As", "state") == "disabled"):
            return
        self.filename = filedialog.asksaveasfilename(initialdir = "~",
                        title = "Select save destination",
                        filetypes = self.myFileTypes,
                        defaultextension = ".anbib")
        if is_empty(self.filename):
            return
        ext = os.path.splitext(self.filename)[1]
        print("Saving file %s"%self.filename)

        with open(self.filename, 'w') as fout:
            if ext == ".anbib":
                self.saveAsAnBib(fout)
            elif ext == ".txt":
                self.saveAsTxt(fout)
            elif ext == ".bib":
                self.saveAsBib(fout)
            else:
                messagebox.showerror("Could Not Save File!", "Could not save file %s"%self.filename)
        self.isSaved = True

    def saveAsAnBib(self, fout):
        fout.write(textwrap.fill("{AUTHOR; "  + self.entries["Author(s)"].get(), 80) + "}\n")
        fout.write(textwrap.fill("{TITLE; "   + self.entries["Title"    ].get(), 80) + "}\n")
        fout.write(textwrap.fill("{JOURNAL; " + self.entries["Journal"  ].get(), 80) + "}\n")
        fout.write(textwrap.fill("{YEAR; "    + self.entries["Year"     ].get(), 80) + "}\n")
        fout.write(textwrap.fill("{VOLUME; "  + self.entries["Volume"   ].get(), 80) + "}\n")
        fout.write(textwrap.fill("{ISSUE; "   + self.entries["Issue"    ].get(), 80) + "}\n")
        fout.write(textwrap.fill("{PAGES; "   + self.entries["Pages"    ].get(), 80) + "}\n")
        fout.write(textwrap.fill("{SUMMARY; "   + self.textEntries["Summary"  ].get('1.0', END), 80) + "}\n")
        fout.write(textwrap.fill("{CRITIQUE; "  + self.textEntries["Critique" ].get('1.0', END), 80) + "}\n")
        fout.write(textwrap.fill("{RELEVANCE; " + self.textEntries["Relevance"].get('1.0', END), 80) + "}\n")

    def saveAsTxt(self, fout):
        fout.write(textwrap.fill("AUTHOR: "  + self.entries["Author(s)"].get(), 80) + "\n")
        fout.write(textwrap.fill("TITLE: "   + self.entries["Title"    ].get(), 80) + "\n")
        fout.write(textwrap.fill("JOURNAL: " + self.entries["Journal"  ].get(), 80) + "\n")
        fout.write(textwrap.fill("YEAR: "    + self.entries["Year"     ].get(), 80) + "\n")
        fout.write(textwrap.fill("VOLUME: "  + self.entries["Volume"   ].get(), 80) + "\n")
        fout.write(textwrap.fill("ISSUE: "   + self.entries["Issue"    ].get(), 80) + "\n")
        fout.write(textwrap.fill("PAGES: "   + self.entries["Pages"    ].get(), 80) + "\n")
        fout.write(textwrap.fill("SUMMARY: "   + self.textEntries["Summary"  ].get('1.0', END), 80) + "\n")
        fout.write(textwrap.fill("CRITIQUE: "  + self.textEntries["Critique" ].get('1.0', END), 80) + "\n")
        fout.write(textwrap.fill("RELEVANCE: " + self.textEntries["Relevance"].get('1.0', END), 80) + "\n")
        print("Saving as %s"%self.filename)

    def saveAsBib(self, fout):
        if (isinstance(self.data, list)):
            for i in range(len(self.data)):
                if not len(self.bib_labels) == len(self.data):
                    label = "article%d"%i
                else:
                    label = self.bib_labels[i][1]
                authors = self.data[i]["AUTHOR"].get().split(",")
                authors = [a.strip() for a in authors] # strip excess white space
                pages = self.data[i]["PAGES"].get().split("-")

                fout.write("@article{ " + label + ",\n")
                fout.write(textwrap.fill("  AUTHOR  = {" + " and ".join(authors), 80) + "},\n")
                fout.write(textwrap.fill("  TITLE   = {" + self.data[i]["TITLE"    ].get(), 80) + "},\n")
                fout.write(textwrap.fill("  JOURNAL = {" + self.data[i]["JOURNAL"  ].get(), 80) + "},\n")
                fout.write(textwrap.fill("  YEAR    = {" + self.data[i]["YEAR"     ].get(), 80) + "},\n")
                fout.write(textwrap.fill("  VOLUME  = {" + self.data[i]["VOLUME"   ].get(), 80) + "},\n")
                fout.write(textwrap.fill("  ISSUE   = {" + self.data[i]["ISSUE"    ].get(), 80) + "},\n")
                fout.write(textwrap.fill("  PAGES   = {" + "--".join(pages), 80) + "},\n}\n")
                fout.write(textwrap.fill("SUMMARY: "   + self.data[i]["SUMMARY"  ].get(), 80) + "\n\n")
                fout.write(textwrap.fill("CRITIQUE: "  + self.data[i]["CRITIQUE" ].get(), 80) + "\n\n")
                fout.write(textwrap.fill("RELEVANCE: " + self.data[i]["RELEVANCE"].get(), 80) + "\n\n")
        else:
            if not len(self.bib_labels) == 1:
                label = "article1"
            else:
                label = self.bib_labels[0][1]

            authors = self.data["AUTHOR"].get().split()
            authors = [a.strip() for a in authors] # strip excess white space
            pages = self.data["PAGES"].get().split("-")

            fout.write("@article{ " + label + ",\n")
            fout.write(textwrap.fill("  AUTHOR  = {" + " and ".join(authors), 80) + "},\n")
            fout.write(textwrap.fill("  TITLE   = {" + self.data["TITLE"    ].get(), 80) + "},\n")
            fout.write(textwrap.fill("  JOURNAL = {" + self.data["JOURNAL"  ].get(), 80) + "},\n")
            fout.write(textwrap.fill("  YEAR    = {" + self.data["YEAR"     ].get(), 80) + "},\n")
            fout.write(textwrap.fill("  VOLUME  = {" + self.data["VOLUME"   ].get(), 80) + "},\n")
            fout.write(textwrap.fill("  ISSUE   = {" + self.data["ISSUE"    ].get(), 80) + "},\n")
            fout.write(textwrap.fill("  PAGES   = {" + "--".join(pages), 80) + "},\n}\n")
            fout.write(textwrap.fill("SUMMARY: "   + self.data["SUMMARY"  ].get(), 80) + "\n")
            fout.write(textwrap.fill("CRITIQUE: "  + self.data["CRITIQUE" ].get(), 80) + "\n")
            fout.write(textwrap.fill("RELEVANCE: " + self.data["RELEVANCE"].get(), 80) + "\n")
            print("Saving as %s"%self.filename)

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
    if platform.system() == "Windows":
        root.wm_state("zoomed")
    elif platform.system() in ["Linux", "Darwin"]:
        root.attributes('-zoomed', True)
    #screen_width = root.winfo_screenwidth()
    #screen_height = root.winfo_screenheight()
    #root.geometry('%sx%s'%(screen_width, screen_height))
    app = App(root)
    root.mainloop()
