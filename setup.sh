#!/usr/bin/env bash

PROJECT_PATH=`pwd`

# check os
uname_out='$(uname -s)'
case '${uname_out}' in
    Linux)      installer='sudo apt install' ;;
    Darwin)     installer='brew install' ;;
    *)          echo 'Your system is not supported, choose installer manually.'
                exit 1
esac

${installer} python3.5


# OpenCV doesn’t play particularly well with virtualenvs,
# so numpy needs to be installed on the system Python
# credit: foxrow.com/installing-opencv-in-a-virtualenv
${installer} python3-numpy
${installer} v4l2loopback-dkms


# set up virtualenv
${installer} virtualenv
virtualenv -p python3.5 env
source env/bin/activate
pip install -r requirements.txt


# install openCV
echo 'Do you want support for DSLR camera? (y/n)'
echo 'y:    compiles and installs openCV with DSLR support (may be unstable)'
echo 'n:    installs openCV from pip, if you use a webcam, use this option'
read custom_install

case '${custom_install}' in
    'y')    deactivate
            cd ${PROJECT_PATH}/config
            ./install-opencv.sh     # only tested on ubuntu
            ln -s /usr/local/lib/python3.5/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so \
                ${PROJECT_PATH}/env/lib/python3.5/site-packages/cv2.so ;;
    'n')    pip install opencv-python ;;
    *)      echo 'Wrong option'
            exit 1
esac

echo 'Installed successfully'
