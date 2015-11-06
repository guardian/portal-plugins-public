#!/usr/bin/env bash

tar cv gnmpurgemeister | gzip > ${HOME}/rpmbuild/gnmpurgemeister.tar.gz
rpmbuild -bb gnmpurgemeister.spec
mv ${HOME}/rpmbuild/RPMS/noarch/portal-purgemeister* .

tar cv gnmplutostats | gzip > ${HOME}/rpmbuild/gnmplutostats.tar.gz
rpmbuild -bb gnmplutostats.spec
mv ${HOME}/rpmbuild/RPMS/noarch/portal-plutostats* .