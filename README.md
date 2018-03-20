# Human detection

# image 
This dir contains experimental codes for the background subtraction and human detection.
Codes in this file work on images.

`main.py` contains several functions to subtract foreground from background.

`main.ipynb` is a jupyter notebook containing codes that detects human in a foreground image.
The image needs to be processed by background subtraction.

Other files doesn't have too much use.

# video
This dir contains codes to be used in the final product. All the codes works on videos.

`backend.py` contains function for processing videos. They are modified from codes in /image.

`model.py` exposes API to GUI(if there is any). It processes video by functions provided by `backend.py`.

`new-controller.py` and `controller.py` are note useful. 
I was about to make a GUI but then took the job of processing videos.
So the half done GUI is left there.
`config.json` contains configurations for the GUI.

If you need to process some video, import `model.py` and use it.

# test-gui
It contains a testing GUI to test functions. For more information look at README inside that dir.


# yuan
This dir contains some code snippets collected by Yuan from the web.
