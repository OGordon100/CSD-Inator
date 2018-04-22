# Import
import cv2
import mss
import numpy as np

# Define game window and area regions
WindowGame = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
WindowsHS = {'top':29,
             'left':[336,458,580,702,824,946,1068,1190],
             'width':112,
             'height':39}

WindowsFood = {'top':105,
             'left':[62,458],
             'width':230,
             'height':58}

# Import comparison images
CompImageHS = cv2.imread('CompHS.png')
CompThresh = 0.9

# Preallocate vectors
ImgWindowsHS = np.zeros([WindowsHS['height'],WindowsHS['width'],3,len(WindowsHS['left'])]).astype('uint8')

# Capture data
sct = mss.mss()
while 'Screen capturing':
    # Get raw pixels from the screen, save it to a Numpy array
    ImgGameWindow = cv2.cvtColor(np.array(sct.grab(WindowGame)), cv2.COLOR_BGRA2RGB)
    
    # Extract holding station regions
    for loopHSCap in range(0,len(WindowsHS['left'])):
        ImgWindowsHS[:,:,:,loopHSCap] = ImgGameWindow[WindowsHS['top']:WindowsHS['top']+WindowsHS['height'],\
                                                   WindowsHS['left'][loopHSCap]:WindowsHS['left'][loopHSCap]+WindowsHS['width'],:]
    
    # Extract hungry people wanting food NOW regions
    
    # For all holding stations
    for loopHSMake in range(0,len(WindowsHS['left'])):
        # Check if empty
        if np.mean(CompImageHS == ImgWindowsHS[:,:,:,loopHSMake]) > CompThresh:
        # Pick a random instruction to fill out
            print('Holding Station ' + str(loopHSMake+1) + ' Free!')
    
    # Test the things that aren't holding stations. 
    
    # Display the game
    #cv2.imshow('Preview Window', ImgWindowHS1)

    # Quit on "q" 
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break