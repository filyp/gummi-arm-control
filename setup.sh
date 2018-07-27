#!/usr/bin/env bash

PROJECT_PATH=`pwd`
export PROJECT_PATH

sudo apt-get install python3.6

# OpenCV doesn’t play particularly well with virtualenvs,
# so numpy needs to be installed on the system Python
# credit: foxrow.com/installing-opencv-in-a-virtualenv
sudo apt-get install python3-numpy

sudo apt-get install virtualenv
virtualenv -p python3.6 env
source env/bin/activate
pip install -r requirements.txt

# custom openCV compilation and installation for Nikon D5100 support
./config/install-opencv.sh
ln -s /usr/local/lib/python3.6/dist-packages/cv2.so \
    ${PROJECT_PATH}/env/lib/python3.6/site-packages/cv2.so
# if you're using a webcam you can use instead:
# pip3 install opencv-python
# which is much faster, because no compilation is needed