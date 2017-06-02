#!/usr/bin/env bash

function increment_release {
    FILENAME=$1

    RELEASEVER=$(grep '%define release' ${FILENAME} | awk -F ' ' '{print $3}')
    if [ ${CIRCLE_BUILD_NUM} != "" ]; then
        NEWVER=${CIRCLE_BUILD_NUM}
    else
        NEWVER=$(($RELEASEVER+1))
    fi
    echo Release version was ${RELEASEVER}, now is ${NEWVER}
    cat ${FILENAME} | sed "s/\%define release .*/%define release ${NEWVER}/" > ${FILENAME}.new
    mv ${FILENAME} ${FILENAME}.old
    mv ${FILENAME}.new ${FILENAME}
}

function build_rpm {
    BASENAME=$1
    SPECFILE="$1.spec"
    if [ ! -f ${SPECFILE} ]; then
        echo "No spec file for ${BASENAME} so can't build"
        return 0    #don't bork things if it failed
    fi
    increment_release ${SPECFILE}
    RPM_BASE=$(grep '%define name' ${SPECFILE} | awk -F ' ' '{print $3}')

	if [ ! -d "${BASENAME}" ]; then
		echo Plugin source dir ${BASENAME} does not exist, cannot continue
		#exit 2
	fi

	echo -----------------------------------------
	echo Compressing ${BASENAME}....
	echo -----------------------------------------
    tar cv ${BASENAME} --exclude .idea | gzip > ${HOME}/rpmbuild/${BASENAME}.tar.gz

    echo -----------------------------------------
    echo Bundling ${BASENAME}....
    echo -----------------------------------------

    rpmbuild -bb ${SPECFILE}

    echo -----------------------------------------
    echo Uploading ${BASENAME}
    echo -----------------------------------------
    if [ "${CIRCLE_TAG}" != "" ]; then
        S3SUBDIR=/public_repo/${CIRCLE_TAG}
    elif [ "${CIRCLE_SHA1}" != "" ]; then
        S3SUBDIR=/public_repo/${CIRCLE_BUILD_NUM}
    else
        S3SUBDIR=/public_repo
    fi

    for x in `ls ${HOME}/rpmbuild/RPMS/noarch/${RPM_BASE}*.rpm`; do
        SHA=$(${SHASUM} $x | cut -f 1 -d ' ')
        echo SHA-256 checksum is ${SHA}
        echo sha256=${SHA} > $x.sha
        aws s3 cp $x s3://gnm-multimedia-deployables/gnm_portal_plugins${S3SUBDIR}/ --acl public-read
        aws s3 cp $x.sha1 s3://gnm-multimedia-deployables/gnm_portal_plugins${S3SUBDIR}/ --acl public-read
    done
}

if [ -x `which shasum` ]; then
    SHASUM=`which shasum`" -a 256"
else
    SHASUM=`which sha256sum`
fi

if [ ! -x "${SHASUM}" ]; then
    echo Unable to locate shasum or sha256sum, can\'t continue.
    exit 1
fi

if [ "$1" == "" ]; then
	for dir in `find . -iname gnm\* -maxdepth 1 -mindepth 1 -type d | awk -F '/' '{ print $2 }' | grep -v -E '^\.'`; do
	    build_rpm $dir
	done
else
	build_rpm $1
fi

#echo ----------------------------
#echo Build completed.  Uploading to S3....
#echo ----------------------------
#echo
#
#for x in `ls *.rpm`; do
#	aws s3 cp "$x" s3://gnm-multimedia-archivedtech/gnm_portal_plugins/$x --acl public-read
#done