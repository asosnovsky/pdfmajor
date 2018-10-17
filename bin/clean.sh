#!/bin/bash
# Get working dir (this will make sure that the script will work the same anywhere you run it)
WK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $WK_DIR
cd ..

rm build -rf
rm dist -rf
rm pdfmajor.egg-info -rf