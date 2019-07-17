#!/bin/bash

# Debug
cat .boto

# setup boto
mv .boto /home/circleci/.boto

## DEBUG
#cat 2600.json

#gsutil ls
if [ "$ENDPOINT" = ""]; then
	ENDPOINT="gs://links.rochester2600.com"
echo "Uploading to $ENDPOINT"
gsutil cp -rp ../build/* $ENDPOINT
