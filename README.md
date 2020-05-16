# Emiglio
My robot buddy

- animations - all face LED animation folders
    -""animation name""
        - "frame_name".png
            - 16x16
        - info.csv
            - #,  "frame_name" -> #  = number of seconds
            - r#, "frame_name" -> r# = max ranom number of seconds of frame
            - 0,#              -> #  = number of repititions for commands since last (0,0)
            - 0,r#             -> #  = max random number of reps for rep cycle
            - 0,0              -> Start new rep cycle
- audio - TODO
- led
    - animations.py
        - Control animations of LEDs on face using animations in "animations" folder
- motor - Normal motors and servo motors
    - ds4_control.py
        - Control robot with PS4 controller (dualshock 4)
    - info.txt
        - servo and motor initialization settings
    - motor.py
        - Motor control class to control speed from PWM PCA9685 and direction from GPIO
    - mover.py
        - Control motor and servo from csv files
    servo.py
        - Servo control for PWM from PCA9685
- movies - Servo control files
    - "movie_name".csv
        - (R Shoulder) (R Elbow) (R Wrist) (L Shoulder) (L Elbow) (L Wrist) (Move Time)
- Power System - General info about power system of robot
- speed - Motor Control Files
    - 'name'.csv
        - (R Front) (R Back) (L Front) (L Back) (Transition time)

__init.py__ - Python package file

__main__.py - Main python module

(led/motor/servo)_sequence.csv - The sequence of the control files to cycle through
                                 Overall Control Files
