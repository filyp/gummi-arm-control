#!/usr/bin/env bash

PROJECT_PATH=`pwd`

brew install python3.5

# OpenCV doesn’t play particularly well with virtualenvs,
# so numpy needs to be installed on the system Python
# credit: foxrow.com/installing-opencv-in-a-virtualenv
brew install python3-numpy
brew install v4l2loopback-dkms

brew install virtualenv
virtualenv -p python3.5 env
source env/bin/activate
pip install -r requirements.txt

# custom openCV compilation and installation for Nikon D5100 support
#deactivate
#cd ${PROJECT_PATH}/config
#./install-opencv.sh
#ln -s /usr/local/lib/python3.5/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so \
#    ${PROJECT_PATH}/env/lib/python3.5/site-packages/cv2.so
# if you're using a webcam you can use instead:
 pip3 install opencv-python
# which is much faster, because no compilation is needed