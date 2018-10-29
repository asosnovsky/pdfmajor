#!/bin/bash
# Get working dir (this will make sure that the script will work the same anywhere you run it)
WK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $WK_DIR
cd ..

./bin/clean.sh

python setup.py sdist bdist_wheel

git add .
git commit
git push

git tag $(cat .version)
git push -u origin $(cat .version)

twine upload dist/*