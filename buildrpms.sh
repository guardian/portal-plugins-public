#!/usr/bin/env bash

function increment_release {
    FILENAME=$1

    RELEASEVER=$(grep '%define release' ${FILENAME} | awk -F ' ' '{print $3}')
    NEWVER=$(($RELEASEVER+1))
    echo Release version was ${RELEASEVER}, now is ${NEWVER}
    cat ${FILENAME} | sed "s/\%define release .*/%define release ${NEWVER}/" > ${FILENAME}.new
    mv ${FILENAME} ${FILENAME}.old
    mv ${FILENAME}.new ${FILENAME}
}

function build_rpm {
    BASENAME=$1
    SPECFILE="$1.spec"
    RPM_BASE=$(grep '%define name' ${SPECFILE} | awk -F ' ' '{print $3}')

	if [ ! -d "${BASENAME}" ]; then
		echo Plugin source dir ${BASENAME} does not exist, cannot continue
		exit 2
	fi
	
    tar cv ${BASENAME} | gzip > ${HOME}/rpmbuild/${BASENAME}.tar.gz
    rpmbuild -bb ${SPECFILE}
    mv ${HOME}/rpmbuild/RPMS/noarch/${RPM_BASE}* .
    increment_release ${SPECFILE}
}

#tar cv gnmplutostats | gzip > ${HOME}/rpmbuild/gnmplutostats.tar.gz
#rpmbuild -bb gnmplutostats.spec
#mv ${HOME}/rpmbuild/RPMS/noarch/portal-plutostats* .
#
#tar cv gnmsyndication | gzip > ${HOME}/rpmbuild/gnmsyndication.tar.gz
#rpmbuild -bb gnmsyndication.spec
#mv ${HOME}/rpmbuild/RPMS/noarch/portal-pluto-gnmsyndication* .

if [ "$1" == "" ]; then
	build_rpm gnmpurgemeister
	build_rpm gnmplutostats
	build_rpm gnmsyndication
else
	build_rpm $1
fi

echo ----------------------------
echo Build completed.  Uploading to S3....
echo ----------------------------
echo

for x in `ls *.rpm`; do
	aws s3 cp "$x" s3://gnm-multimedia-archivedtech/gnm_portal_plugins --acl public-read
done