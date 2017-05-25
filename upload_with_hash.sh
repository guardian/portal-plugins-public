#!/bin/bash

if [ -x /bin/shasum ]; then
    SHASUM="/bin/shasum -a 256"
else
    SHASUM="/bin/sha256sum"
fi

SHA=$(${SHASUM} $1  | cut -f 1 -d ' ')
echo SHA-256 checksum is ${SHA}
echo sha256=${SHA} > $1.sha

aws s3 cp $1 $2
aws s3 cp $1.sha $2.sha