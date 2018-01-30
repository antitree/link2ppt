#!/bin/bash

# setup boto
mv .boto /home/circleci/.boto

## DEBUG
#cat 2600.json

#gsutil ls
ENDPOINT="gs://links.rochester2600.com"
echo "Uploading to $ENDPOINT"
gsutil cp -p ../build/* $ENDPOINT
