# Import
import cv2
import mss
import numpy as np
import pytesseract
import pyautogui
import random
import re
import time


# Define function to extract a region of the game window
def WindowExtractor (BigWindow,WindowBounds,BoundNumX,BoundNumY):
    return BigWindow[WindowBounds['top'][BoundNumY]:WindowBounds['top'][BoundNumY]+WindowBounds['height'],\
                     WindowBounds['left'][BoundNumX]:WindowBounds['left'][BoundNumX]+WindowBounds['width'],:]

# Define function to scan game window
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

# Define function to build a set of instructions to follow
def InstructionMaker (RawInstruction):
    RecipeInstructions = []
    for IngredientItem in RawInstruction.split("  "):
        
        # Get ingredient name
        Ingredient = IngredientItem.split(" (")[0]
        
        # Get number of repeat keypresses
        RepeatSearch = re.search(r'[0-9]',IngredientItem)
        if RepeatSearch:
            RepeatNum = int(RepeatSearch.group(0))          
        else:
            RepeatNum = 1         
        
        # Get key to press: if not in special list, just take first letter
        if Ingredient in SpecialKeyBinds:
            KeyCombo = SpecialKeyBinds[Ingredient]
        else:
            KeyCombo = Ingredient[0].lower()
        
        # Build the instruction!
        RecipeInstructions.append([Ingredient, RepeatNum, KeyCombo])
    return(RecipeInstructions)   

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
             'height':115}

# Define non-obvious keypresses
SpecialKeyBinds = {'Chicken':'k' , 'Scrambled':'c' , 'Popcorn Shrimp':'p',
                   'Shrimp':'h' , 'Corn':'r' , 'Ground Meat':'m' , 
                   'Onions':'n' , 'Red Beans':'b' , 'Carrots':'a' , 
                   'Lobster':'b' , 'Clam Bits':'l' , 'S.Pork':'p' ,
                   'Wh.Rice':'r' , 'G.Beans':'e' , 'Bowtie N.':'n' ,
                   'B.Tortilla':'t' , 'B.Broccoli':'r' , 'Wheat B.':'h' ,
                   'Close':'l' , 'Turkey':'u' , 'Paper Liner':'n' , 
                   'Blueberry':'l' , 'Banana':'a', 'Chocolate':'a' , 
                   'Raw Chop':'l' , 'Sauce':'a' , "Pig's Blood":'b' , 
                   'Fine Peanut':'p' , 'P.Onions':'n' , 'Cauliflower':'a' , 
                   'Cucumber':'u' , 'Cut Parsley':'p' , 'Choc. Cr':'h' , 
                   'Coconut Mer.':'o' , 'Coconut Shav.':'o' , 'Covered':'v' , 
                   'R.Chow. Mein':'h' , 'O.Shoots':'s' , 'Cucumbers':'u' , 
                   'Butter':'u' , 'Black Beans':'a' , 'Cooking Oil':'o' , 
                   'Chow Mein':'h' , 'Wheat Bread':'h' , 'Steak Fr.':'t' , 
                   'Shoestring':'h' , 'Onion Rings':'n' , 'D.Potatoes':'p' , 
                   'Paprika':'r' , 'Black Rice':'r' , 'Brown Rice':'r' , 
                   'Corn':'r' , 'Croutons':'r' , 'Mixed Veg':'v' , 
                   'Tuscan Beans':'b' , 'Candy Cookie':'a' , 'White Rice':'r' ,
                   'Wild Rice':'r' , 'Soy Sauce':'o' , 'Clam':'l'} 

# Set stuff up
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
ImgWindowsHS = np.zeros([WindowsHS['height'],WindowsHS['width'],3,len(WindowsHS['left'])]).astype('uint8')
DoneOpts1 = []
DoneOpts2 = []
HS_Capturing = 1
AllRecipeOpts = [] 
sct = mss.mss()

# Find and store holding station options
while HS_Capturing == 1:
    # Take constant images of screen until a Holding Station appears 
    ImgGameWindow = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
    if np.round(np.mean(WindowExtractor(ImgGameWindow,WindowsHS,1,0))) == 38.0:
        # Open the holding station
        print('Capturing holding station data!')
        pyautogui.keyDown('tab')  
        pyautogui.keyDown('1')
        time.sleep(.300)
        pyautogui.keyUp('tab')
        pyautogui.keyUp('1')
        
        # OCR for each page of the holding station, and store results
        for loopRecipeBuilder in range(0, 3):
            ImgCapt = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
            AllRecipeOpts.append(TextScan(ImgCapt,WindowsTextRegions))
            pyautogui.keyDown('space')
            pyautogui.keyUp('space')
            HS_Capturing = 0
        
        # Leave holding station
        pyautogui.keyDown('enter')
        pyautogui.keyUp ('enter')
        break
    
# Give animations time to finish, so first HS is 1, not 2.
time.sleep(2)

# A NEW DAY OF FEASTING IS AT HAND
while 'Screen capturing':
    # Get raw pixels from the screen, save it to a numpy array
    ImgGameWindow = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
    
    # Extract holding station regions
    for loopHSCap in range(0,len(WindowsHS['left'])):
        ImgWindowsHS[:,:,:,loopHSCap] = WindowExtractor(ImgGameWindow,WindowsHS,loopHSCap,0)
        
    # Extract hungry people wanting food NOW regions
    
    # For each holding station
    for loopHSMake in range(0,len(WindowsHS['left'])):
        # Check if a HS is free 
        if np.round(np.mean(ImgWindowsHS[:,:,:,loopHSMake])) == 38.0:
            print('\nHolding Station ' + str(loopHSMake+1) + ' Free!')
                        
            # Open the holding station (can't use.hotkey because of releasing keys backwards)
            pyautogui.keyDown('tab')  
            pyautogui.keyDown(str(loopHSMake+1))
            time.sleep(.300)
            pyautogui.keyUp('tab')
            pyautogui.keyUp(str(loopHSMake+1))
            
            # Pick a recipe
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
                    # Make a HS optional recipe
                    print('Making a HS optional recipe')
                    randopt = random.sample(FiltOpts2,1)[0].lower()
                    DoneOpts2.append(randopt.upper())
                else:
                    # Make a side
                    print('All HS optional recipes made \nMaking a side')
                    RecipeOpts = AllRecipeOpts[2]
                    HSWindowNum += 1
                    pyautogui.hotkey('space')
                    randopt = random.sample(RecipeOpts,1)[0].lower()
            else:         
                break
            
            # Start the recipe!!!
            print('    Making Recipe ' + randopt.upper())
            pyautogui.keyDown(randopt)
            pyautogui.keyUp(randopt)
            
            # Threshold and scan for instructions
            time.sleep(2)
            ImgInstructionInputBig = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
            ImgInstruction =cv2.cvtColor(WindowExtractor(ImgInstructionInputBig,WindowsFoodRecipe,0,0),cv2.COLOR_RGB2GRAY)
            ImgInstruction[ImgInstruction==213] = 255 
            ImgInstruction[ImgInstruction!=255] = 0 
            wordstoremove = re.compile(r'\W*\b\w{1,1}\b')
            RawInstruction = pytesseract.image_to_string(ImgInstruction,config='-psm 11').replace('\n', ' ').replace('ENTER','')
            #sRawInstruction = wordstoremove.sub('', RawInstruction)
            print('    Found Recipe: ' + RawInstruction)
            
            # Get number of red, blue, green instructions
            
            # Build out list to perform
            AllInstructions = InstructionMaker(RawInstruction)
            print('    Instructions: ' + " ".join(str(elm) for elm in AllInstructions))
            
            # Perform instructions
            for Instruction in AllInstructions:
                for PressKey in range(0,Instruction[1]):
                    pyautogui.keyDown(Instruction[2])
                    pyautogui.keyUp(Instruction[2])
                                        
            # Finish recipe
            pyautogui.press('enter')
            
            break
