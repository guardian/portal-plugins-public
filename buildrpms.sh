#!/usr/bin/env bash

rpmbuild -bb gnmpurgemeister.spec
mv ${HOME}/rpmbuild/RPMS/noarch/portal-purgemeister* .
