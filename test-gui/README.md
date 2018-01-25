# What is this?

This is a test GUI for testing your functions.

[example](./example.gif)

# Install

You need to install pyqt5 and opencv-python

# Run

To run the program, simply execute ```main-controller.py```

# Configure

I have several test functions predefined as examples. 
In order to include your function into GUI:

1. put your function into ```model.py```
   Your function has to be in this format:
   1. the first argument is a image_boxes (list),
   it contains four image_box objects.
   You can get images by ```image_box.image```
   For example, I get the second image by ```iamge_boxes[1].image```
   2. save your images to the desired on. 
   In this example I saved the output to ```image_boxes[2].image```
   3. You have to return a string indicating the status of the function.
   It can be anything: "failed", "done", "wrong image", etc
   4. images in image_box have to be RGB images.
   In this example I first converted RGB image to gray scale image,
   process it, then convert it back to RGB image and saved to image_box.

    ```python
    def threshold(image_boxes, threshold=177, max_value=255):
        image = cv2.cvtColor(image_boxes[1].image, cv2.COLOR_RGB2GRAY)
        ret, threshold_result = cv2.threshold(image, threshold, max_value,
cv2.THRESH_BINARY)
        image_boxes[2].image = cv2.cvtColor(threshold_result, cv2.COLOR_GRAY2RGB)
        return 'threshold done'
    ```

2. Once you have the function in ```model.py```,
   go to ```main-controller.py``` and find a variable called ```avaliable_functions```.
   In this dict the key is the name you want to use for your function,
   and the value is the actually function is ```model.py```.

   ```python
       avaliable_functions = {
        "threshold": model.threshold,
        "canny": model.canny,
    }
    ```
3. For the other arguments that goes after image_boxes, put them into ```config.json```
   In `config.json`, there is a dict called ```functions```,
   that's where all the configureations go.
   In this example "canny" is the name of the function,
   and the two lists are arguments that will be passed 
   into function you just provided in ```model.py``` after image_boxes
   So when the first variant of canny is called, it looks like
   ```canny(iamge_boxes, 200, 250)```

   ```json
       "functions": {
        "canny":
        [
            [200, 250],
            [200, 300]
        ],
        "threshold":
        [
            [177, 225],
            [177, 225]
        ]
    }
    ```

