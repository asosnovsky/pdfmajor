#!/bin/bash
# Get working dir (this will make sure that the script will work the same anywhere you run it)
WK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $WK_DIR
cd ..

# for filename in ./tests/test*.py; do
#     if python $filename ; then
#         echo woohoo
#     else
#         exit 1
#     fi
# done

if python ./test.py ; then
    echo "PASSED TESTS"
else
    exit 1
fi