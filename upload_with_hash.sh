#!/bin/bash -e

#if [ -x `which shasum` ]; then
#    SHASUM="`which shasum` -a 256"
#else
#    SHASUM="`which sha256sum`"
#fi
SHASUM=/usr/bin/sha256sum

SHA=$(${SHASUM} $1  | cut -f 1 -d ' ')
echo SHA-256 checksum is ${SHA}
echo sha256=${SHA} > $1.sha

aws s3 cp --acl=public-read $1 $2
aws s3 cp --acl=public-read $1.sha $2.sha