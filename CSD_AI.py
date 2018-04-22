# Import
import cv2
import mss
import numpy as np
import pytesseract
import pyautogui
import random
import re
import time

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'

# Define game window and area regions
WindowGame = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
WindowsHS = {'top':[29],
             'left':[336,458,580,702,824,946,1068,1190],
             'width':112,
             'height':39}

WindowsWaiting = {'top':[105],
             'left':[62,458],
             'width':230,
             'height':58}

WindowsTextRegions = {'top':[155,245,340,430],
             'left':[1625,1785],
             'width':48,
             'height':48}

WindowsFoodRecipe = {'top':[875],
             'left':[460],
             'width':1000,
             'height':155}

# Define function to extract a region of the game window
def WindowExtractor (BigWindow,WindowBounds,BoundNumX,BoundNumY):
    return BigWindow[WindowBounds['top'][BoundNumY]:WindowBounds['top'][BoundNumY]+WindowBounds['height'],\
                     WindowBounds['left'][BoundNumX]:WindowBounds['left'][BoundNumX]+WindowBounds['width'],:]

def TextScan (ImgGame,WindowBounds):
                # Take image and binarise to extract detail
                ImgFoodInputBig = ImgGame 
                ImgFoodInputBig[(ImgFoodInputBig[:,:,0]==ImgFoodInputBig[:,:,1]) & (ImgFoodInputBig[:,:,0]==ImgFoodInputBig[:,:,2])] = 255
                WindowBig = [ImgFoodInputBig!=[255,255,255]][0].astype('uint8')*255
                
                # Find all avaliable keypresses
                RecipeOpts = []
                IterFindOpts = 0
                for loopImgFindx in range(0,len(WindowsTextRegions['left'])):
                    for loopImgFindy in range(0,len(WindowsTextRegions['top'])):
                        ImgInput = WindowExtractor(WindowBig,WindowBounds,loopImgFindx,loopImgFindy)
                        FoundThing = pytesseract.image_to_string(ImgInput[:,:,0],config='-psm 10')
                        if FoundThing != '':
                            RecipeOpts.append(FoundThing)
                        IterFindOpts += 1
                return(RecipeOpts)

# Import comparison images
CompImageHS = cv2.imread('CompImages\CompHS.png')
CompThresh = 0.9

# Set stuff up
ImgWindowsHS = np.zeros([WindowsHS['height'],WindowsHS['width'],3,len(WindowsHS['left'])]).astype('uint8')
DoneOpts1 = []
DoneOpts2 = []
HS_Capturing = 1
AllRecipeOpts = [] 

sct = mss.mss()

# Find and store holding station options
while HS_Capturing == 1:
    ImgGameWindow = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
    if np.mean(CompImageHS == WindowExtractor(ImgGameWindow,WindowsHS,1,0)) > CompThresh:
        print('Capturing holding station data!')
        pyautogui.keyDown('tab')  
        pyautogui.keyDown('1')
        time.sleep(.300)
        pyautogui.keyUp('tab')
        pyautogui.keyUp('1')
        for loopRecipeBuilder in range(0, 3):
            ImgCapt = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
            #cv2.imshow('test',ImgCapt)
            AllRecipeOpts.append(TextScan(ImgCapt,WindowsTextRegions))
            pyautogui.keyDown('space')
            pyautogui.keyUp('space')
            HS_Capturing = 0
         
        pyautogui.keyDown('enter')
        pyautogui.keyUp ('enter')
        break
time.sleep(2)

# BEGIN
while 'Screen capturing':
    # Get raw pixels from the screen, save it to a Numpy array
    ImgGameWindow = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
    
    # Extract holding station regions
    for loopHSCap in range(0,len(WindowsHS['left'])):
        ImgWindowsHS[:,:,:,loopHSCap] = WindowExtractor(ImgGameWindow,WindowsHS,loopHSCap,0)
    # Extract hungry people wanting food NOW regions
    
    # For each holding station

    for loopHSMake in range(0,len(WindowsHS['left'])):
        # Check if a HS is free (NB- change this to just look for white text!)
        if np.mean(CompImageHS == ImgWindowsHS[:,:,:,loopHSMake]) > CompThresh:
            print('\nHolding Station ' + str(loopHSMake+1) + ' Free!')
                        
            # Open the holding station (can't use.hotkey because of releasing keys backwards)
            pyautogui.keyDown('tab')  
            pyautogui.keyDown(str(loopHSMake+1))
            time.sleep(.300)
            pyautogui.keyUp('tab')
            pyautogui.keyUp(str(loopHSMake+1))
            
            # Pick an option
            HSWindowNum = 1
            FiltOpts1 = set(AllRecipeOpts[0])-set(DoneOpts1)
            FiltOpts2 = set(AllRecipeOpts[1])-set(DoneOpts2)
            if (HSWindowNum == 1) & (bool(FiltOpts1) == 1):
                # Make a HS required recipe
                print('Making a HS required recipe')
                randopt = random.sample(FiltOpts1,1)[0].lower()
                DoneOpts1.append(randopt.upper())
            elif (bool(FiltOpts1) == 0):
                print('All HS required recipes made')
                HSWindowNum += 1
                pyautogui.hotkey('space')
                RecipeOpts = AllRecipeOpts[1]
                if (HSWindowNum == 2) & (bool(FiltOpts2) == 1):
                    # Make a HS required recipe
                    print('Making a HS optional recipe')
                    randopt = random.sample(FiltOpts2,1)[0].lower()
                    DoneOpts2.append(randopt.upper())
                else:
                    print('All HS optional recipes made. Making a side')
                    RecipeOpts = AllRecipeOpts[2]
                    HSWindowNum += 1
                    pyautogui.hotkey('space')
                    randopt = random.sample(RecipeOpts,1)[0].lower()
            else:         
                break
            
            # Start the recipe!!! 
            pyautogui.keyDown(randopt)
            pyautogui.keyUp(randopt)
            
            # Threshold and scan for instructions
            ImgInstructionInputBig = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
            ImgInstruction =cv2.cvtColor(WindowExtractor(ImgInstructionInputBig,WindowsFoodRecipe,0,0),cv2.COLOR_RGB2GRAY)
            ImgInstruction[ImgInstruction!=255] = 0 
            
            # Parse raw instructions into ordered list
            RawInstruction = pytesseract.image_to_string(ImgInstruction)
            
            # For each task
            try:
                NumPresses = np.asarray(re.findall('\((.*?)\)',RawInstruction)).astype(np.int)[0]
            except:
                NumPresses = 1
            KeyPress = RawInstruction[0].lower()
            
            # Get number of purple, red, green instructions
            for loopPressKey in range(0,NumPresses):
                pyautogui.keyDown(KeyPress)
                pyautogui.keyUp(KeyPress)
            pyautogui.press('enter')
            
            break
    
