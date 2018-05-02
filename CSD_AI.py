##### IMPORT ####
import cv2
import mss
import numpy as np
import pytesseract
import pyautogui
import random
import re
import time

##### FUNCTIONS ####

# Define function to extract a region of the game window
def WindowExtractor (BigWindow,WindowBounds,BoundNumX,BoundNumY):
    return BigWindow[WindowBounds['top'][BoundNumY]:WindowBounds['top'][BoundNumY]+WindowBounds['height'],\
                     WindowBounds['left'][BoundNumX]:WindowBounds['left'][BoundNumX]+WindowBounds['width'],:]

# Define function to threshold and determine number of recipes for the holding stations
def TextScanHSOpts (ImgGame,WindowBounds):
                # Take image and binarise to extract detail
                ImgFoodInputBig = ImgGame 
                ImgFoodInputBig[(ImgFoodInputBig[:,:,0]==ImgFoodInputBig[:,:,1]) & (ImgFoodInputBig[:,:,0]==ImgFoodInputBig[:,:,2])] = 255
                WindowBig = [ImgFoodInputBig!=[255,255,255]][0].astype('uint8')*255
                
                # Window out chores?
                
                # Find all avaliable keypresses
                RecipeOpts = []
                IterFindOpts = 0
                for loopImgFindx in range(0,len(WindowsTextRegions['left'])):
                    for loopImgFindy in range(0,len(WindowsTextRegions['top'])):
                        ImgInput = WindowExtractor(WindowBig,WindowBounds,loopImgFindx,loopImgFindy)

                        FoundThing = pytesseract.image_to_string(ImgInput[:,:,0],config='-psm 10')
                        
                        # Add code here to deal with chores
                        
                        # Turn into parsed raw text
                        if FoundThing != '':
                            RecipeOpts.append(FoundThing)
                        IterFindOpts += 1
                return(RecipeOpts)

# Define function to follow through recipe finding & creation
def FoodMaker (WindowGame,WindowRegion):
    # Threshold and scan for instructions
    RawInstruction = TextScanRecipe(WindowGame,WindowRegion)
    print('            Raw Text: ' + str(RawInstruction[0]))
    
    # Build out list to perform
    AllInstructions = InstructionMaker(RawInstruction)
    print('            Instructions: ' + " ".join(str(elm) for elm in AllInstructions))
    
    # Perform instructions
    InstructionFollower(AllInstructions)
    time.sleep(0.1)

# Define function to threshold and determine ingredients avaliable for a recipe
def TextScanRecipe (WindowGame,WindowsFoodRecipe): 
    time.sleep(0.1)
    
    # Get image
    ImgInstructionInputBig = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
    ImgInstructionRGB = WindowExtractor(ImgInstructionInputBig,WindowsFoodRecipe,0,0)      
    ImgInstruction = cv2.cvtColor(ImgInstructionRGB,cv2.COLOR_RGB2GRAY)
    # Get number of purple, red, yellow instructions
    NumPurple = int(np.round(np.sum(cv2.inRange(ImgInstructionRGB,np.array([201,65,122]),np.array([201,65,122])))/ColourBlobSize))
    NumRed = int(np.round(np.sum(cv2.inRange(ImgInstructionRGB,np.array([65,65,201]),np.array([65,65,201])))/ColourBlobSize))
    NumYellow = int(np.round(np.sum(cv2.inRange(ImgInstructionRGB,np.array([41,138,189]),np.array([41,138,189])))/ColourBlobSize))
    PageNums = [NumPurple,NumRed,NumYellow]
    
    # Get raw instruction    
    ImgInstruction[ImgInstruction==213] = 255 
    ImgInstruction[ImgInstruction==192] = 255
    ImgInstruction[ImgInstruction!=255] = 0 
    RawInstruction = pytesseract.image_to_string(ImgInstruction,config='-psm 11').replace('\n', ' ').replace('ENTER','')
    return(RawInstruction,PageNums)
    
# Define function to build a set of instructions to follow
def InstructionMaker (RawInstruction):
    RecipeInstructions = []

    # If chore:
    if RawInstruction[0] in ChoreInstructions:
        RecipeInstructions = ChoreInstructions[RawInstruction[0]]
        
    # If not chore:
    else:
        for IngredientItem in RawInstruction[0].split("  "):
            
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
         
        # Add in instructions to go to new page if neccessary
        if RawInstruction[1][1] == 0 & RawInstruction[1][0] != 0 & RawInstruction[1][2] != 0:
            NumFilled = 2
        else:
            NumFilled = sum(x != 0 for x in RawInstruction[1]) - 1
        RawInstructionFilt = RawInstruction[1][0:NumFilled]
        for SpaceInsert in RawInstructionFilt[::-1]:
            RecipeInstructions.insert(SpaceInsert,['NextPage',1,'space'])
    
    # Return
    return(RecipeInstructions)   

# Define function to follow instructions
def InstructionFollower (AllInstructions):
    # Follow instructions in list
    for Instruction in AllInstructions:
                    for PressKey in range(0,Instruction[1]):
                        pyautogui.keyDown(Instruction[2])
                        pyautogui.keyUp(Instruction[2])
                                            
    # Finish recipe
    pyautogui.press('enter')
    
##### SETTINGS ####

# Define game window and area regions
WindowGame = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
WindowsHS = {'top':[29],
             'left':[336,458,580,702,824,946,1068,1190],
             'width':112,
             'height':39}
WindowsServeRegion = {'top':[102,168,234,300,366,432,498,564,630,696,762,828,894,960],
             'left':[0],
             'width':44,
             'height':56}
WindowsCookRegion = {'top':[131,197,263,329,395,461,527,593,659,725,791,857,923,989],
             'left':[66],
             'width':258,
             'height':33}
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
                   'Blueberry':'l' , 'Banana':'a', 'Chocolate':'h' , 
                   'Raw Chop':'l' , 'Sauce':'a' , "Pig's Blood":'b' , 
                   'Fine Peanut':'p' , 'P.Onions':'n' , 'Cauliflower':'a' , 
                   'Cucumber':'u' , 'Cut Parsley':'p' , 'Choc. Cr.':'h' , 
                   'Coconut Mer.':'o' , 'Coconut Shav.':'o' , 'Covered':'v' , 
                   'R.Chow. Mein':'h' , 'O.Shoots':'s' , 'Cucumbers':'u' , 
                   'Butter':'u' , 'Black Beans':'a' , 'Cooking Oil':'o' , 
                   'Chow Mein':'h' , 'Wheat Bread':'h' , 'Steak Fr.':'t' , 
                   'Shoestring':'h' , 'Onion Rings':'n' , 'D.Potatoes':'p' , 
                   'Paprika':'r' , 'Black Rice':'r' , 'Brown Rice':'r' , 
                   'Corn':'r' , 'Croutons':'r' , 'Mixed Veg':'v' , 
                   'Tuscan Beans':'b' , 'Candy Cookie':'a' , 'White Rice':'r' ,
                   'Wild Rice':'r' , 'Soy Sauce':'o' , 'Clam':'l', 
                   'Raw Chop':'l' , 'Gr. Chicken':'k' , 'Top Bun':'o' , 
                   'Guacemole':'u' , 'Sprouts':'p' , 'Pineapple':'i' , 
                   'Avocado':'v' , 'Peas':'e' , 'Cranberry':'r' , 
                   'Spicy Chk.':'s' , 'Biscuit':'i' , 
                   'Croissant':'r' , 'Pecan':'e' , 'S.Pasta':'p' , 
                   'Grd.Meat':'m' , 'B.Sugar':'s' , 'Chili':'h' , 
                   'Lobster Sauce':'o' , 'Citrus Mayo':'m' , 'Lemon Aioli':'a',
                   'Arti.Sauce':'r', 'C.Apple':'a' , 'Drumstick':'r' , 
                   'Oysters':'y' , 'Caviar':'a' , 'Cocktail':'o' , 
                   'C.Dates':'d' , 'C.Green':'g' , 'C.Red':'r' , 'C.White':'w',
                   'C.Tamarind':'t' , 'Peach':'e' , 'Texas':'x' , 
                   'Pretzel Bun':'z' , 'Pumpkin':'u' , 'Olives':'v' ,
                   'Refried Beans':'b' , 'Black Beans':'a' , 'Guac':'u' ,
                   'S.Mushrooms':'m' , 'S.Onions':'n' , 'Fr.iEgg':'e' , 
                   'Peppermint':'m' , 'Choc.Chips':'h' , 'Caramel':'a' , 
                   'P.Sugar':'s' , 'Chocolate S.':'o' , 'Blueberries':'l' , 
                   'Choe Crisps':'h' , 'Texas Tea':'x' , '[tsl':'r' ,
                   'After placing the ingredients. Dunk & Cook.':'d' ,
                   'Peach Tea':'e'} 

ChoreInstructions = {'The restroom needs attention. thank you.':[['Flush', 1, 'f'],['Sanitise', 1, 's']] , 
                     'Throw the trash. Thanks!':[['Throw', 1, 't'],['Sanitise', 1, 's']] , 
                     'Throw the trash, Be sure to mash it in there!':[['Throw', 1, 't'],['Mash', 20, 'm'],['Sanitise', 1, 's']] ,
                     'Please set the roach traps. thank you.':[['Set Traps', 1, 't'],['Sanitise', 1, 's']] ,
                     'Please set the rat traps. thank you.':[['Lock', 1, 'l'],['Cheese', 1, 'c'],['Set', 1,'s']] ,
                     'Load the dirty dishes into the rack. Wash. wait for the green light. and then  release the washer and unload the dishes.':[['Dishes', 1, 'd'],['Wash', 30, 'w'],['Release', 1,'r'],['Unload', 1,'u'],['Sanitise', 1,'s']] ,
                     'Please clean the pest light trap. thank you.':[['Open Trap', 1, 't'],['Close Trap', 1, 'c'],['Sanitise', 1, 's']]}

ServingKeyBinds = {'1':'1' , '2':'2' , '3':'3' , '4':'4' , '5':'5' , '6':'6' ,
                   '7':'7' , '8':'8' , '9':'9' , '10':'0' , '11':'-' , 
                   '12':'=' , '13':'[' , '14':']'}

# Set stuff up
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'
sct = mss.mss()
HS_Capturing = 1
ImgWindowsHS = np.zeros([WindowsHS['height'],WindowsHS['width'],3,len(WindowsHS['left'])]).astype('uint8')
ImgWindowsServe = np.zeros([WindowsServeRegion['height'],WindowsServeRegion['width'],3,len(WindowsServeRegion['top'])]).astype('uint8')
DoneOpts1 = []
DoneOpts2 = []
DoneOpts11 = []
DoneOpts22 = []
AllRecipeOpts = [] 
pyautogui.PAUSE = 0.07
PauseTime = 0.07
ColourBlobSize = 155040     # Number of pixels a purple/red/yellow blow takes up

##### DETERMINE HS OPTIONS ####

# Find and store holding station options
while HS_Capturing == 1:
    # Take constant images of screen until a Holding Station appears 
    ImgGameWindow = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
    if int(np.round(np.mean(WindowExtractor(ImgGameWindow,WindowsHS,1,0)))) in range(36,40):
        # Open the holding station
        print('Capturing holding station data!')
        pyautogui.keyDown('tab')  
        time.sleep(PauseTime)
        pyautogui.keyDown('1')
        time.sleep(PauseTime)
        pyautogui.keyUp('tab')
        time.sleep(PauseTime)
        pyautogui.keyUp('1')
        
        # OCR for each page of the holding station, and store results
        for loopRecipeBuilder in range(0, 3):
            ImgCapt = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
            AllRecipeOpts.append(TextScanHSOpts(ImgCapt,WindowsTextRegions))
            pyautogui.keyDown('space')
            pyautogui.keyUp('space')
            HS_Capturing = 0
        
        # Leave holding station
        pyautogui.keyDown('enter')
        pyautogui.keyUp ('enter')
        break
    
# Start with a side to increase waiting time
pyautogui.keyDown('tab')  
time.sleep(PauseTime)
pyautogui.keyDown('6')
time.sleep(PauseTime)
pyautogui.keyUp('tab')
time.sleep(PauseTime)
pyautogui.keyUp('6')
pyautogui.hotkey('space')
pyautogui.hotkey('space')
pyautogui.keyDown('a')
pyautogui.keyUp('a')    
FoodMaker(WindowGame,WindowsFoodRecipe)

# A NEW DAWN OF FEASTING IS AT HAND
start_time = time.time()
while 'Screen capturing':
    # Get raw pixels from the screen, save it to a numpy array
    ImgGameWindow = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_RGBA2RGB)
        
    for loopHSCap in range(0,len(WindowsHS['left'])):
        ImgWindowsHS[:,:,:,loopHSCap] = WindowExtractor(ImgGameWindow,WindowsHS,loopHSCap,0)

    # For each holding station (but not at rush hour)
    elapsed_time = time.time() - start_time   
    if elapsed_time < 90 or int(elapsed_time) in range(160,250) or elapsed_time > 310:
        for loopHSMake in range(0,len(WindowsHS['left'])):
            
            # Check if a HS is free 
            if int(np.round(np.mean(ImgWindowsHS[:,:,:,loopHSMake]))) in range(36,40):
                print('\nHolding Station ' + str(loopHSMake+1) + ' Free!')
                            
                # Open the holding station (can't use.hotkey because of releasing keys backwards)
                pyautogui.keyDown('tab')  
                time.sleep(PauseTime)
                pyautogui.keyDown(str(loopHSMake+1))
                time.sleep(PauseTime)
                pyautogui.keyUp('tab')
                time.sleep(PauseTime)
                pyautogui.keyUp(str(loopHSMake+1))
                
                # Create list of already completed options, but remove from list if we are revisiting the HS that option was made in
                for RemoverLoop1 in DoneOpts11:
                   if RemoverLoop1[1] == loopHSMake+1:
                       DoneOpts1.remove(RemoverLoop1[0])
                       DoneOpts11.remove(RemoverLoop1)
                for RemoverLoop2 in DoneOpts22:
                   if RemoverLoop2[1] == loopHSMake+1:
                       DoneOpts2.remove(RemoverLoop2[0])
                       DoneOpts22.remove(RemoverLoop2)                
                FiltOpts1 = set(AllRecipeOpts[0])-set(DoneOpts1)
                FiltOpts2 = set(AllRecipeOpts[1])-set(DoneOpts2)
                
                # Pick a recipe
                HSWindowNum = 1
                if (HSWindowNum == 1) & (bool(FiltOpts1) == 1) & (len(AllRecipeOpts[0]) > 0):
                    # Make a HS required recipe
                    print('    Making a HS required recipe')
                    randopt = random.sample(FiltOpts1,1)[0].lower()
                    DoneOpts1.append(randopt.upper())
                    DoneOpts11.append([randopt.upper(),loopHSMake+1])
                elif (bool(FiltOpts1) == 0):
                    print('    All HS required recipes made')
                    HSWindowNum += 1
                    pyautogui.hotkey('space')
                    RecipeOpts = AllRecipeOpts[1]
                    if (HSWindowNum == 2) & (bool(FiltOpts2) == 1) & (len(AllRecipeOpts[1]) > 0):
                        # Make a HS optional recipe
                        print('    Making a HS optional recipe')
                        randopt = random.sample(FiltOpts2,1)[0].lower()
                        DoneOpts2.append(randopt.upper())
                        DoneOpts22.append([randopt.upper(),loopHSMake+1])
                    elif (len(AllRecipeOpts[2]) > 0):
                        # Make a side
                        print('    All HS optional recipes made \n    Making a side')
                        RecipeOpts = AllRecipeOpts[2]
                        HSWindowNum += 1
                        pyautogui.hotkey('space')
                        randopt = random.sample(RecipeOpts,1)[0].lower()
                else:
                    print('    Nothing to make in a HS!')
                    break
                
                # Start the recipe!!!
                print('        Making Recipe ' + randopt.upper())
                pyautogui.keyDown(randopt)
                pyautogui.keyUp(randopt)
                
                FoodMaker(WindowGame,WindowsFoodRecipe)
        
    # For each serving region
    for loopServeRegionCap in range(0,len(WindowsServeRegion['top'])):
        ImgWindowsServe[:,:,:,loopServeRegionCap] = WindowExtractor(ImgGameWindow,WindowsServeRegion,0,loopServeRegionCap)
    
    for loopServeRegionMake in range(0,len(WindowsServeRegion['top'])):
        # Check if a serving region requires service
        if np.sum(ImgWindowsServe[:,:,:,loopServeRegionMake] == [255,255,255]) > 0:
            print('\nServing Station ' + str(loopServeRegionMake+1) + ' Occupied!')
            
            # Get section of screen
            ImgServeRegion = WindowExtractor(ImgGameWindow,WindowsCookRegion,0,loopServeRegionMake)
            
            # Determine if food can be served, or is currently cooking
            if np.sum(cv2.inRange(ImgServeRegion,np.array([255,255,255]),np.array([255,255,255]))) > 45000:
                # If food is currently cooking, do nothing
                print('    Blocked/Waiting for Cooking.')
            #elif np.sum(cv2.inRange(ImgServeRegion,np.array([0,36,255]),np.array([0,36,255]))) > 750:     
            #    # If food currently waiting for HS required stage, do nothing
            #    print('    Food is waiting for HS.')
            else:    
                # Attempt to insta-serve
                pyautogui.keyDown(ServingKeyBinds[str(loopServeRegionMake+1)])
                time.sleep(PauseTime)
                pyautogui.keyUp(ServingKeyBinds[str(loopServeRegionMake+1)])
                
                ImgInstaTester = WindowExtractor(cv2.cvtColor(np.array(sct.grab(WindowGame)), 
                                                         cv2.COLOR_RGBA2RGB),WindowsFoodRecipe,0,0)
                if np.sum(cv2.inRange(ImgInstaTester,np.array([73,73,73]),np.array([73,73,73]))) < 1000: 
                    print('        Food insta-served')
                else:
                    # If extra steps required
                    print('        Extra steps required')
                    FoodMaker(WindowGame,WindowsFoodRecipe)
                    
# Need to look for burning food and prioritise it!
