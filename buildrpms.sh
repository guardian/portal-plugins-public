#!/usr/bin/env bash

function increment_release {
    FILENAME=$1

    RELEASEVER=$(grep '%define release' ${FILENAME} | awk -F ' ' '{print $3}')
    if [ ${CIRCLE_SHA1} != "" ]; then
        NEWVER=${CIRCLE_SHA1}
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
    tar cv ${BASENAME} | gzip > ${HOME}/rpmbuild/${BASENAME}.tar.gz

    echo -----------------------------------------
    echo Bundling ${BASENAME}....
    echo -----------------------------------------

    rpmbuild -bb ${SPECFILE}

    echo -----------------------------------------
    echo Uploading ${BASENAME}
    echo -----------------------------------------
    aws s3 cp ${HOME}/rpmbuild/RPMS/noarch/${RPM_BASE}*.rpm s3://gnm-multimedia-archivedtech/gnm_portal_plugins/${BASENAME}/$x --acl public-read
    #mv ${HOME}/rpmbuild/RPMS/noarch/${RPM_BASE}* .
}

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