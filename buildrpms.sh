#!/bin/bash -e

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

	if [ ! -d "portal/plugins/${BASENAME}" ]; then
		echo Plugin source dir ${BASENAME} does not exist, cannot continue
		return 0 #don't bork things if it failed
		#exit 2
	fi

	echo -----------------------------------------
	echo Compressing ${BASENAME}....
	echo -----------------------------------------
    tar cv portal/plugins/${BASENAME} --exclude .idea | gzip > ${HOME}/rpmbuild/SOURCES/${BASENAME}.tar.gz

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
        aws s3 ls s3://gnm-multimedia-deployables
        aws s3 cp $x s3://gnm-multimedia-deployables/gnm_portal_plugins${S3SUBDIR}/`basename $x` --region eu-west-1 --acl public-read
        aws s3 cp $x.sha s3://gnm-multimedia-deployables/gnm_portal_plugins${S3SUBDIR}/`basename $x.sha` --region eu-west-1  --acl public-read
    done
}

SHASUM="/usr/bin/sha256sum"


if [ ! -d "${HOME}/rpmbuild" ]; then
    mkdir -p ${HOME}/rpmbuild/SOURCES
fi

if [ "$1" == "" ]; then
	for dir in `find portal/plugins -maxdepth 1 -mindepth 1 -type d | awk -F '/' '{ print $3 }' | grep -v -E '^\.'`; do
	    if [ "${CIRCLE_BUILD_NUM}" != "" ]; then
	        echo "build_number=${CIRCLE_BUILD_NUM}" > portal/plugins/$dir/version.py
	    fi
	    build_rpm $dir
	done
else
	build_rpm $1
fi