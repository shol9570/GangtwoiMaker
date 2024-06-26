import cv2 as cv
import numpy as np
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showinfo
import tkinter.messagebox
import tkinter.font as tkfont
import pyglet
from PIL import Image, ImageTk, ImageDraw, ImageFont
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def MakeGangtwoi(name: str, mode: int=0):
    global maskImg, bg_mk1, bg_mk2, btnImg
    global resultImg

    targetBG = None
    if mode == 0:
        targetBG = bg_mk1
    elif mode == 1:
        targetBG = bg_mk2
    else:
        return

    filename = askopenfilename(filetypes=[("all", "*"), ("jpg", ".jpg"), ("png", ".png")])
    if filename == "":
        return 0
    stream = open(filename, 'rb')
    bytes = bytearray(stream.read())
    numpyarray = np.asarray(bytes, dtype=np.uint8)
    
    # Load image
    img = cv.imdecode(numpyarray, cv.IMREAD_UNCHANGED)
    img = cv.cvtColor(img, cv.COLOR_BGR2BGRA)
    img_h, img_w = img.shape[:2]

    bg_h, bg_w = targetBG.shape[:2]

    # Resize image
    dsize_h = 263
    dsize_w = 263
    resized = cv.resize(img, dsize=(dsize_h, dsize_w), interpolation=cv.INTER_LINEAR)
    resized_h, resized_w = resized.shape[:2]

    # Masking
    masked = resized.copy()
    masked[maskImg < 10] = 0
    masked[maskImg >= 10] = resized[maskImg >= 10]

    # Rebase image
    img_rebase = np.zeros_like(targetBG, np.uint8)
    rebase_y = 15
    rebase_x = 142
    rebase_h = min(bg_h-rebase_y, dsize_h)
    rebase_w = min(bg_w-rebase_x, dsize_w)
    img_rebase[rebase_y:min(rebase_y+dsize_h, bg_h), rebase_x:min(rebase_x+dsize_w, bg_w)] = masked[:rebase_h, :rebase_w]
    #cv.imshow('rebased', img_rebase)

    # Add rebased image to bg
    result = targetBG.copy()
    result[img_rebase[:,:,3] != 0] = img_rebase[img_rebase[:,:,3] != 0]
    
    # Add btn
    result[btnImg[:,:,3] == 255] = cv.addWeighted(result, 0, btnImg, 1, 0)[btnImg[:,:,3] == 255]
    
    result_height, result_width = result.shape[:2]

    font = ImageFont.truetype(fontPath, 40)
    result_pil = Image.fromarray(result)
    draw = ImageDraw.Draw(result_pil)
    draw.text((276,324), name, fill=(0,0,0,255), font=font, anchor="mm", align="center")
    result = np.array(result_pil)

    resultImg = result.copy()
    gangtwoiBtn["state"] = "normal"

    result = cv.cvtColor(result, cv.COLOR_BGRA2RGBA)
    result = Image.fromarray(result)
    tkImg = ImageTk.PhotoImage(image=result)

    imgLabel.configure(image=tkImg)
    imgLabel.image = tkImg

    win.maxsize(width=result_width, height=result_height+50)
    win.geometry("{width}x{height}".format(width=result_width,height=result_height+50))

def resize_image(event):
    global resultImg
    
    if resultImg is None:
        return
    
    img_h, img_w = resultImg.shape[:2]
    imgRatio = img_w / img_h
    width = event.width
    height = int(width / imgRatio)
    if height > event.height:
        height = event.height
        width = (int)(height * imgRatio)

    tempImg = cv.resize(resultImg, dsize=(width, height))
    tempImg = cv.cvtColor(tempImg, cv.COLOR_BGRA2RGBA)
    tempImg = Image.fromarray(tempImg)
    tkImg = ImageTk.PhotoImage(image=tempImg)

    imgLabel.configure(image=tkImg)
    imgLabel.image = tkImg

def Save_Image():
    global resultImg

    if resultImg is None:
        return
    
    savePath = asksaveasfilename(title="강퇴", defaultextension=".jpg", filetypes=[("jpg", ".jpg"), ("png", ".png"), ("All files", "*")])
    if savePath == "":
        return
    cv.imwrite(savePath, resultImg)

def AnimateSword(currentFrame=0):
    global imgLabel, resultImg, frames, gifImgs
    if resultImg is not None:
        return
    cut = gifImgs[currentFrame]
    imgLabel.configure(image=cut)
    imgLabel.image=cut
    currentFrame += 1
    if currentFrame == frames:
        currentFrame = 0
    imgLabel.after(50, lambda: AnimateSword(currentFrame))

def EntyCallback(var, index, mode):
    if var == "":
        return
    UpdateGangTwoiBtnState()

def GangtwoiTypeListComboboxEvent(event):
    UpdateGangTwoiBtnState()

def UpdateGangTwoiBtnState():
    global gangtwoiTypeList, generateGangtwoiBtn, textboxTxt
    if textboxTxt.get() != "" and gangtwoiTypeList.current() >= 0:
        generateGangtwoiBtn["state"] = "normal"
    else:
        generateGangtwoiBtn["state"] = "disabled"

def main():
    global maskImg, bg_mk1, bg_mk2, btnImg
    global win, topFrame, bottomFrame
    global fontPath, normalFont
    global textbox, gangtwoiTypeList, generateGangtwoiBtn, gangtwoiBtn, infoBtn, imgLabel
    global resultImg

    # Initialize variables
    fontPath = resource_path('./Resources/font.ttf')

    # Load images
    maskImg = cv.imread(resource_path('./Resources/mask.jpg'), cv.IMREAD_GRAYSCALE)
    bg_mk1 = cv.imread(resource_path('./Resources/bg_mk1.jpg'), cv.IMREAD_UNCHANGED)
    bg_mk1 = cv.cvtColor(bg_mk1, cv.COLOR_BGR2BGRA)
    bg_mk2 = cv.imread(resource_path('./Resources/bg_mk2.jpg'), cv.IMREAD_UNCHANGED)
    bg_mk2 = cv.cvtColor(bg_mk2, cv.COLOR_BGR2BGRA)
    btnImg = cv.imread(resource_path('./Resources/btn.png'), cv.IMREAD_UNCHANGED)

    # Tkinter initialize
    win = tk.Tk(screenName='GangtwoiMaker', baseName=None, className='tk', useTk=1, sync=0, use=None)
    win.title('GangtwoiMaker')
    win.geometry('500x250')
    win.minsize(width=500, height=250)
    win.maxsize(width=800, height=250)
    winSize_X = win.winfo_reqwidth()
    winSize_Y = win.winfo_reqheight()

    # Tkinter font
    pyglet.font.add_file(fontPath)
    normalFont=tkfont.Font(family='카카오 Regular', size=10, weight='normal')

    topFrame = tk.Frame(win, height=2)
    topFrame.pack(side="top", fill="x", expand=False)
    bottomFrame = tk.Frame(win)
    bottomFrame.pack(side="bottom", fill="both", expand=True)

    global textboxTxt
    textboxTxt = tk.StringVar()
    textboxTxt.trace_add("write", EntyCallback)
    textbox = tk.Entry(topFrame, textvariable=textboxTxt)
    textbox.pack(side="left", fill="both", expand=True)

    gangtwoiTypeList = ttk.Combobox(topFrame, values=('강퇴 Mk1', '강퇴 Mk2'), width=8, height=2, font=normalFont, state="readonly")
    gangtwoiTypeList.set("강퇴 유형")
    gangtwoiTypeList.pack(side="left", fill="y", expand=False)
    gangtwoiTypeList.bind("<<ComboboxSelected>>", GangtwoiTypeListComboboxEvent)
        
    generateGangtwoiBtn = tk.Button(topFrame, text="강퇴", highlightcolor='cyan', width=4, height=2, command=lambda: MakeGangtwoi(textboxTxt.get(), gangtwoiTypeList.current()), font=normalFont, state="disabled")
    generateGangtwoiBtn.pack(side="left", fill="y", expand=False)

    gangtwoiBtn = tk.Button(topFrame, text="내보내기", highlightcolor='cyan', width=8, height=2, command=lambda: Save_Image(), font=normalFont, state="disabled")
    gangtwoiBtn.pack(side="left", fill="y", expand=False)

    infoStr = """========================================

    Program: GangtwoiMaker
    Author: SHOL
    Version: v1.3.1

    The MIT License (MIT)

    Copyright (c) 2024 SHOL
    
    Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
    
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

    ========================================"""

    infoBtn = tk.Button(topFrame, text="i", highlightcolor='cyan', width=2, height=2, command=lambda: showinfo("GangtwoiMaker info", infoStr), font=normalFont)
    infoBtn.pack(side="left", fill="y", expand=False)

    resultImg = None
    imgLabel = tk.Label(bottomFrame, image=None)
    imgLabel.pack(fill="both", anchor="n", expand=True)
    imgLabel.bind('<Configure>', resize_image)

#region Animated idle window
    gifFile = Image.open(resource_path('./Resources/gangtwoisword.gif'))

    global frames
    frames = gifFile.n_frames

    global gifImgs
    gifImgs = []
    for i in range(frames):
        cutImg = tk.PhotoImage(file=resource_path('./Resources/gangtwoisword.gif'), format=f"gif -index {i}")
        gifImgs.append(cutImg)
    
    AnimateSword(0)
#endregion

    win.mainloop()

# Global variables
global maskImg, bg_mk1, bg_mk2, btnImg
global win, topFrame, bottomFrame
global fontPath, normalFont
global textbox, gangtwoiTypeList, generateGangtwoiBtn, gangtwoiBtn, infoBtn, imgLabel
global resultImg

if __name__ == "__main__":
    main()