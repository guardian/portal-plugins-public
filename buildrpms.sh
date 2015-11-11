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
    RPM_BASE=$(grep '%define name' ${SPECFILE} | aws -F ' ' '{print $3}')

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

build_rpm gnmpurgemeister
build_rpm gnmplutostats
build_rpm gnmsyndication