#!/bin/sh
#
#
mkdir website/processing/files
mkdir website/processing/errors
mkdir website/processing/tmp
cp data/*.pickle website/processing/files/.
chown www-data.www-data -R /home/ubuntu/CanLink/code/website/processing/
