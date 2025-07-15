from tkinter import messagebox, ttk
from tkinter import Entry
from tkinter.filedialog import askopenfilename
import tkinter
import shelve
PIDS = 0
INSTANCES: dict[int, tkinter.Toplevel] = {}
def focusIn(PID): INSTANCES[PID].overrideredirect(False); INSTANCES[PID].state(newstate='normal'); INSTANCES[PID].overrideredirect(True); return True
def focusOut(PID): INSTANCES[PID].overrideredirect(False); INSTANCES[PID].state(newstate='iconic'); INSTANCES[PID].overrideredirect(True); return True
def focusMaximise(PID): INSTANCES[PID].attributes("-topmost", True)
WIDGETS = {}
FRAMES: dict[int, list[tkinter.Frame]] = {}
BUTTON_FRAMES: dict[int, tkinter.Frame] = {}
MAIN_FRAMES: dict[int, tkinter.Text] = {}
NEEDS_FILESYSTEM_ACCESS = True
THEME_WINDOW_BG, THEME_FOREGROUND = ["Black", "White"]

SepKeyWIDGETSTORES: dict[int, list[dict[str, list[Entry]], dict[str, list[Entry]], int]] = {}

def constructBackDict(PID, loadDict: dict, shelvePath: str=None, entryWidgetToChange: Entry = None):
    MAIN_DICT = {}
    keyStore = SepKeyWIDGETSTORES[PID][0]
    valueStore = SepKeyWIDGETSTORES[PID][1]
    for o, item in enumerate(keyStore.keys()):
        try:
            kT = eval(keyStore[item][1].get())
            if kT in (list, tuple, dict, set, bool): k = eval(keyStore[item][0].get())
            else: k = kT((keyStore[item][0].get()))
            vT = eval(valueStore[item][1].get())
            if vT in (list, tuple, dict, set, bool): v = eval(valueStore[item][0].get())
            else: v = vT((valueStore[item][0].get()))
            MAIN_DICT[k] = v
        except Exception as EXP:
            messagebox.showerror("Can't generate new dict", f"Can't generate the new dict, at iteration for key {item}\nMerging as original types!\nEXP:{EXP}")
            keyIndex = list(dict(loadDict).keys())[o]
            MAIN_DICT[keyIndex] = list(dict(loadDict).values())[o]
    if entryWidgetToChange:
        entryWidgetToChange.delete(0, tkinter.END)
        entryWidgetToChange.insert(tkinter.END, str(MAIN_DICT))
    else: 
        if not shelvePath: return str(MAIN_DICT)
        BACKUP_DICT = {}
        with shelve.open(shelvePath, writeback=True) as writer:
            BACKUP_DICT.update(dict(writer))
            writer.clear()
            writer.update(MAIN_DICT)
        if messagebox.askyesno("Do you want a backup?", "Do you want to save a backup of the original file?"):
            with shelve.open(shelvePath+"_BACKUP.dat", writeback=True) as backup:
                print(BACKUP_DICT)
                backup.clear()
                backup.update(BACKUP_DICT)

    return str(MAIN_DICT)

def dictView(PrID, loadedDict: dict, shelvePath: str, callFromKey: str = None,):
    dctToIterate = None
    PID = PrID
    global PIDS
    ROOT = INSTANCES[PrID]
    if callFromKey: 
        print(loadedDict)
        dctToIterate = dict(loadedDict)
        InternalPID = PIDS+1
        INSTANCES[InternalPID] = ROOT = topLevel = tkinter.Toplevel(INSTANCES[PrID], background=THEME_WINDOW_BG)
        PID = InternalPID
        PIDS +=1
    else: 
        dctToIterate = dict(loadedDict)
        path = shelvePath.replace("\\", "/")
        INSTANCES[PID].title("Shelve Editor")
        INSTANCES[PID].title(path.split("/")[-1] + " - " + INSTANCES[PID].title())
    if PID not in SepKeyWIDGETSTORES.keys(): SepKeyWIDGETSTORES[PID] = [{}, {}, 0]
    WIDGET_KEY_STORE, WIDGET_VALUE_STORE, LOOPNUM = SepKeyWIDGETSTORES[PID]
    if len(WIDGET_VALUE_STORE) or len(WIDGET_KEY_STORE):
        for widgetLs in WIDGET_KEY_STORE.values(): 
            for item in widgetLs: item.destroy()
        for widgetLs in WIDGET_VALUE_STORE.values():
            for item in widgetLs: item.destroy()
        WIDGET_VALUE_STORE.clear()
        WIDGET_KEY_STORE.clear()
        for children in FRAMES[PID][4].winfo_children(): children.destroy()
        del FRAMES[PID]



    KEY_STORE = {}
    VALUE_STORE = {}
    print(PID)
    if PID in MAIN_FRAMES.keys(): 
        for children in MAIN_FRAMES[PID].winfo_children(): children.destroy()
    else:
        MAIN_FRAMES[PID] = tkinter.Text(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND)
        MAIN_FRAMES[PID].configure(state="disabled")
        MAIN_FRAMES[PID].grid(row=2, column=0)
    scrollbar = ttk.Scrollbar(ROOT, command=MAIN_FRAMES[PID].yview)
    scrollbar.grid(row=2, column=5, sticky="NES", rowspan=5)
    tkinter.Label(MAIN_FRAMES[PID], background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Key Type").grid(row=2, column=0)
    tkinter.Label(MAIN_FRAMES[PID], background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Key").grid(row=2, column=1)
    tkinter.Label(MAIN_FRAMES[PID], background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Value Type").grid(row=2, column=2)
    tkinter.Label(MAIN_FRAMES[PID], background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Value").grid(row=2, column=3)
    if not PID in FRAMES.keys(): FRAMES[PID] = [tkinter.Frame(MAIN_FRAMES[PID], background=THEME_WINDOW_BG), tkinter.Frame(MAIN_FRAMES[PID], background=THEME_WINDOW_BG), tkinter.Frame(MAIN_FRAMES[PID], background=THEME_WINDOW_BG), tkinter.Frame(MAIN_FRAMES[PID], background=THEME_WINDOW_BG), tkinter.Frame(MAIN_FRAMES[PID], background=THEME_WINDOW_BG)]
    keyTypeFrame, keyFrame, valueTypeFrame, valueFrame, removeKeyFrame = FRAMES[PID]
    keyTypeFrame.grid(row=3, column=0)
    keyFrame.grid(row=3, column=1)
    valueTypeFrame.grid(row=3, column=2)
    valueFrame.grid(row=3, column=3)
    removeKeyFrame.grid(row=3, column=4)
    cmd = lambda: constructBackDict(PID,loadedDict, shelvePath)
    if callFromKey: cmd = lambda: constructBackDict(PID, loadedDict, shelvePath, SepKeyWIDGETSTORES[PrID][1][callFromKey][0])
    saveButton = tkinter.Button(BUTTON_FRAMES[PID], background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Save Dict!", command=cmd)
    saveButton.grid(row=0, column=2)

    for i, keys in enumerate(dctToIterate.keys()):
        SepKeyWIDGETSTORES[PID][2] += 1
        FONT = ("Calibri", 14)
        widget = Entry(keyFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=50)
        widget.insert(tkinter.END, str(keys))
        widget.grid(row=i, column=0)
        typeFr = Entry(keyTypeFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=20,) 
        typeFrActual = str(type(keys))[8:-2]
        typeFr.insert(tkinter.END, typeFrActual)
        typeFr.grid(row=i, column=0)
        KEY_STORE[keys] = typeFrActual
        WIDGET_KEY_STORE[keys] = [widget, typeFr]
        valWidth = 100
        if isinstance(dctToIterate[keys], (dict, shelve.Shelf)): 
            valWidth = 85
            button = tkinter.Button(valueFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Edit Dict", command=lambda f=keys: dictView(PID, dctToIterate[f], shelvePath, f), justify="right", width=10, font=("Calibri", 6))
            button.grid(row=i, column=0, sticky="E")
        value = Entry(valueFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=valWidth, justify='left',)
        value.insert(tkinter.END, str(dctToIterate[keys]))
        value.grid(row=i, column=0, sticky="W")
        typeVal = Entry(valueTypeFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=20)
        typeValActual = str(type(dctToIterate[keys]))[8: -2]
        typeVal.insert(tkinter.END, typeValActual)
        typeVal.grid(row=i, column=0)
        VALUE_STORE[keys] = typeValActual
        if isinstance(dctToIterate[keys], (dict, shelve.Shelf)):  WIDGET_VALUE_STORE[keys] = [value, typeVal, button]
        else: WIDGET_VALUE_STORE[keys] = [value, typeVal]
        removeKB = tkinter.Button(removeKeyFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Remove Key", command= lambda k=keys: removeKey(PID, k),font=("Calibri", 6),)
        removeKB.grid(row=i, column=0)
    newKeyButton = tkinter.Button(BUTTON_FRAMES[PID], text="Add a new key!", background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, command=lambda: addNewKey(PID, loadedDict, callFromKey) )
    newKeyButton.grid(row=0, column=1)
    if callFromKey: topLevel.mainloop()

def removeKey(PID: int, keyToRemove: str):
    for widget in SepKeyWIDGETSTORES[PID][0][keyToRemove]: widget.destroy()
    for widget in SepKeyWIDGETSTORES[PID][1][keyToRemove]: widget.destroy()
    del SepKeyWIDGETSTORES[PID][0][keyToRemove]
    del SepKeyWIDGETSTORES[PID][1][keyToRemove]

def openFile(PID: int):
    filepath = askopenfilename(parent=INSTANCES[PID], title="Open any shelve file (It will not consider extensions don't worry)", filetypes=(("Shelve Data File", "*.dat"), ("Shelve Bak Files", "*.bak"), ("Shelve Dir Files", "*.dir"),("All Files", "*.*")),)
    if isinstance(filepath, str): filepath = filepath.rstrip(".dir").rstrip(".bak").rstrip(".dat")
    DICT = None
    try:
        with shelve.open(filepath) as reader: DICT = dict(reader)
        if not len(DICT.keys()) or not len(DICT.values()): raise Exception
    except Exception: 
        try: 
            with shelve.open(filepath+".dat") as reader: DICT = dict(reader)
            if not len(DICT.keys()) or not len(DICT.values()): raise Exception
        except Exception: messagebox.showerror("Cannot read file!", "The selected file cannot be read!")
        else: dictView(PID, DICT, filepath)
    else: dictView(PID, DICT, filepath)

def _actualAddKey(PID, LoadedDict, KT, K, VT, V, callFromKey: str=None):
    kT = eval(KT)
    if kT in (list, tuple, dict, set, bool): k = eval(K)
    else: k = kT(K)
    keyTypeFrame, keyFrame, valueTypeFrame, valueFrame, removeKeyFrame = FRAMES[PID]
    widget = Entry(keyFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=50)
    SepKeyWIDGETSTORES[PID][2]+=1
    widget.insert(tkinter.END, K)
    widget.grid(row=SepKeyWIDGETSTORES[PID][2], column=0)
    typeFr = Entry(keyTypeFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=20) 
    typeFr.grid(row=SepKeyWIDGETSTORES[PID][2], column=0)
    typeFr.insert(tkinter.END, KT)
    valWidth = 100
    value = Entry(valueFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=valWidth, justify='left')
    value.grid(row=SepKeyWIDGETSTORES[PID][2], column=0, sticky="W")
    value.insert(tkinter.END, V)
    typeVal = Entry(valueTypeFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=20)
    typeVal.grid(row=SepKeyWIDGETSTORES[PID][2], column=0)
    typeVal.insert(tkinter.END, VT)
    SepKeyWIDGETSTORES[PID][0].update({k: [widget, typeFr]})
    SepKeyWIDGETSTORES[PID][1].update({k: [value, typeVal]})
    removeKB = tkinter.Button(removeKeyFrame, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Remove Key", command= lambda k=k: removeKey(PID, k),font=("Calibri", 6),)
    removeKB.grid(row=SepKeyWIDGETSTORES[PID][2], column=0)

def addNewKey(PID, LoadedDict, callFromKey: str=None):
    ROOT = tkinter.Toplevel(INSTANCES[PID], background=THEME_WINDOW_BG)
    txt = "MAIN"
    if callFromKey: txt=callFromKey
    ROOT.title(f"Add New Key Wizard [Target: {txt}]")

    tkinter.Label(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Key Type").grid(row=1, column=0)
    tkinter.Label(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Key").grid(row=1, column=1)
    tkinter.Label(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Value Type").grid(row=1, column=2)
    tkinter.Label(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Value").grid(row=1, column=3)

    keyTypeWidget = Entry(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=20)
    keyTypeWidget.grid(row=2, column=0)
    keyWidget = Entry(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=50)
    keyWidget.grid(row=2, column=1)
    valTypeWidget = Entry(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=20)
    valTypeWidget.grid(row=2, column=2)
    valWidget = Entry(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, width=100)
    valWidget.grid(row=2, column=3)

    addKeyBtn = tkinter.Button(ROOT, background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Add the key!", command=lambda: _actualAddKey(PID, LoadedDict, keyTypeWidget.get(), keyWidget.get(), valTypeWidget.get(), valWidget.get(), callFromKey))
    addKeyBtn.grid(row=3, column=0)

    ROOT.mainloop()

def main(*args):
    global PIDS
    INSTANCES[0] = tkinter.Tk()
    THEME_WINDOW_BG, THEME_FOREGROUND = ["Black", "White"]
    INSTANCES[0].configure(background=THEME_WINDOW_BG)
    INSTANCES[0].title("Shelve Editor")
    PIDS += 1
    BUTTON_FRAMES[0] = tkinter.Frame(INSTANCES[0], background=THEME_WINDOW_BG)
    BUTTON_FRAMES[0].grid(row=1, column=0, sticky="W")
    openFileButton = tkinter.Button(BUTTON_FRAMES[0], background=THEME_WINDOW_BG, foreground=THEME_FOREGROUND, text="Open a shelve file!", command=lambda PID=0: openFile(PID))
    openFileButton.grid(row=0, column=0)
    INSTANCES[0].mainloop()

if __name__ == '__main__': main()
