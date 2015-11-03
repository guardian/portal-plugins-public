#!/usr/bin/env bash

tar cv gnmpurgemeister | gzip > ${HOME}/rpmbuild/gnmpurgemeister.tar.gz
rpmbuild -bb gnmpurgemeister.spec
mv ${HOME}/rpmbuild/RPMS/noarch/portal-purgemeister* .
