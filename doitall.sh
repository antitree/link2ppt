#!/bin/bash
python2 l2ppt.py -i creds -r 2600.md
cp 2600.md ../rochester2600-hugo/static/files/2600.md
cd ../rochester2600-hugo
git commit static/files/2600.md -m 'updating monthly 2600 links'
echo "REady to deploy but too scared to do it automatically."
read -p "Are you ready to push changes? " -n 1 -r
if [[ $REPLY =~ ^[Yy]$ ]]
then
    ./deploy.sh
fi
