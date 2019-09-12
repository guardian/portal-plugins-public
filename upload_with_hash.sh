#!/bin/bash -e

SHASUM=/usr/bin/sha256sum

SHA=$(${SHASUM} $1  | cut -f 1 -d ' ')
echo SHA-256 checksum is ${SHA}
echo sha256=${SHA} > $1.sha

set | grep AWS

aws s3 cp --acl=public-read $1 $2
aws s3 cp --acl=public-read $1.sha $2.sha