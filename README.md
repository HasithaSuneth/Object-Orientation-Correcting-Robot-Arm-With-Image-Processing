# Objects Orientation Correcting Robot Arm with Image Processing (OpenCV)

This is the final year project of the Higher National Diploma in Electrical & Electronic Engineering (ICBT Campus). This project mainly focused on to correct orientation of the ice cream cups before moving to the manufacturing details label printing machine. 

A Digital web camera with raspberry pie is used to identify the current object orientation of the object and correct object orientation with the robot arm.

<p align="center">
  <img width="500" src="https://user-images.githubusercontent.com/87106402/164913939-25f7afdc-cb04-4f5e-8881-f02a8b379828.png" alt="Block Diagram">
</p>

# How it operates

Design starts showing main menu with three user input choices (Figure 02), after system get powered. Users have to place object (ice cream cup) at default orientation under the PiCamera module and need to press “Default image take” button for capture that orientation (Figure 03). System moves back to main menu, after captured default orientation. After that, system can use to correct orientation of the object, based on object default orientation.

<p align="center">
  <img width="500" src="https://user-images.githubusercontent.com/87106402/164914075-46d2b66d-a1aa-4e5e-bf05-6970a1418efa.png" alt="Block Diagram">
</p>

Design has two main modes, as name as Auto mode (Figure 04) & Manual mode (Figure 05). In Manual mode, User need to press “Mode” button every time after randomly orientated object placed under the camera for correct orientation of the object. In Auto mode, User doesn’t need to press “Mode” button frequently, after placed object under the camera. Program automatically identify object and begin to further procedures. User need to press and hold “Mode” button 3 seconds for activate Auto mode.

<p align="center">
  <img width="500" src="https://user-images.githubusercontent.com/87106402/164914160-78fccfb8-3c11-49ed-a4db-d656fd8b88ad.png" alt="Block Diagram">
</p>

Program run OpenCV based color detection algorithm for identify orientation of object. Orientation value display on LCD and send it to Arduino for correct physical object orientation using Robotic arm.

<p align="center">
  <img width="500" src="https://user-images.githubusercontent.com/87106402/164914745-2fe5a8ff-7669-43d5-926a-f59cda9495c0.png" alt="Block Diagram">
</p>

After correct orientation of the object and system in manual mode, program move back to main menu and wait for user action. If system in auto mode, Program move back to object detection section and wait for another object.

# Detailed Explanation
1. CAPTURE DEFAULT ORIENTATION OF THE OBJECT

OpenCV image capturing algorithm use for capture object image, after get input from “Default Image Take” button. Flash lights use for light up object and get better quality image. Canny edge detection algorithm uses to crop image and remove unnecessary free space from the image.

2. IDENTIFYING OBJECT

Image color detection algorithm used specified color section on the object to identify it. This algorithm continuously read live frames, convert them into HSV color format and create mask using preconfigured color range. Algorithm identify and capture the object image, if specified color arrived to the center of the frame.

3. IDENTIFYING CORRECT ORIENTATION OF THE OBJECT

<p align="center">
  <img width="500" src="https://user-images.githubusercontent.com/87106402/164915667-cc77215b-f8ab-46b4-85e8-402625481643.png" alt="Block Diagram">
</p>

Canny edge detection algorithm used to crop the image captured from identifying object function and stored in SD card. Preconfigured color detection algorithm uses to create two masks from cropped default orientation object image and cropped rotated object image. Mask 2 rotate 1˚ degree at a time and save it in the lists data structure using ‘for loop’ till complete 360˚ degree. Mask 1 subtracts with lists items (mask 2) and count sum of black pixels from subtract result. Correct orientation gives from statues of highest black pixel count. Index value of lists data structure use to get correct orientation angel using subtract result.
