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

# TODO check if it can be simplified
# OpenCV doesn’t play particularly well with virtualenvs,
# so numpy needs to be installed on the system Python
# credit: foxrow.com/installing-opencv-in-a-virtualenv
${installer} python3-numpy


# set up virtualenv
${installer} virtualenv
virtualenv -p python3.5 env
source env/bin/activate
pip install -r requirements.txt
pip install opencv-python

echo 'Installed successfully'
