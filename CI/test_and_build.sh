#!/usr/bin/bash -e

source ~/.bashrc
BUILDDIR=$(pwd)
declare -x CI=1

echo ===================================================
echo Installing prerequisites....
echo ===================================================

yum -y install which; pip install virtualenv
mkdir -p ~/virtualenvs/portal-plugins-public

echo ===================================================
echo Installing JSX dependencies....
echo ===================================================
yarn install


echo ===================================================
echo Preparing Python build....
echo ===================================================
virtualenv ~/virtualenvs/portal-plugins-public
source ~/virtualenvs/portal-plugins-public/bin/activate
pip install nose pep8 >/dev/null
pip install -r test-requirements.txt >/dev/null

echo ===================================================
echo Installing gnmvidispine....
echo ===================================================
mkdir -p ~/fredex42/gnmvidispine
git clone https://github.com/fredex42/gnmvidispine  ~/fredex42/gnmvidispine
cd  ~/fredex42/gnmvidispine; source ~/virtualenvs/portal-plugins-public/bin/activate && python setup.py install >/dev/null
declare -x PYTHONPATH=~/fredex42/gnmvidispine:$PYTHONPATH

echo ===================================================
echo Installing build-specific components....
echo ===================================================
cd $BUILDDIR
touch portal/__init__.py; touch portal/plugins/__init__.py
mkdir -p /opt/cantemo/portal/portal/plugins
for dir in `find portal/plugins -maxdepth 1 -mindepth 1 -type d | grep -v -E '^\.'`; do echo Symlinking ${dir} to build locations; ln -s ${PWD}/$dir /opt/cantemo/portal/portal/plugins;done
for dir in `find portal/plugins -maxdepth 1 -mindepth 1 -type d | grep -v -E '^\.'`; do echo Trying to run "${PWD}/$dir/testsetup.sh"; if [ -x "${PWD}/$dir/testsetup.sh" ]; then ${PWD}/$dir/testsetup.sh; fi; done

echo ===================================================
echo Testing generic javascript....
echo ===================================================
### all plugins
cd $BUILDDIR/portal/plugins
npm run test
npm run lint
npm run testcss
cd $BUILDDIR

echo ===================================================
echo gnmpagerduty....
echo ===================================================
DJANGO_SETTINGS_MODULE=portal.plugins.gnmpagerduty.tests.django_test_settings  ~/virtualenvs/portal-plugins-public/bin/nosetests -v portal/plugins/gnmpagerduty/tests --xunit-file=${CIRCLE_TEST_REPORTS}/gnmpagerduty.xml

echo ===================================================
echo gnmlibrarytool....
echo ===================================================
DJANGO_SETTINGS_MODULE=portal.plugins.gnmlibrarytool.tests.django_test_settings  ~/virtualenvs/portal-plugins-public/bin/nosetests -v portal/plugins/gnmlibrarytool/tests --xunit-file=${CIRCLE_TEST_REPORTS}/gnmlibrarytool.xml

echo ===================================================
echo gnmatomresponder....
echo ===================================================
DJANGO_SETTINGS_MODULE=portal.plugins.gnmatomresponder.tests.django_test_settings  ~/virtualenvs/portal-plugins-public/bin/nosetests -v portal/plugins/gnmatomresponder/tests --xunit-file=${CIRCLE_TEST_REPORTS}/gnmatomresponder.xml

echo ===================================================
echo gnmoptin....
echo ===================================================
DJANGO_SETTINGS_MODULE=portal.plugins.gnmoptin.tests.django_test_settings  ~/virtualenvs/portal-plugins-public/bin/nosetests -v portal/plugins/gnmoptin/tests --xunit-file=${CIRCLE_TEST_REPORTS}/gnmoptin.xml

echo ===================================================
echo gnmplutostats....
echo ===================================================
DJANGO_SETTINGS_MODULE=portal.plugins.gnmplutostats.tests.django_test_settings  ~/virtualenvs/portal-plugins-public/bin/nosetests -v portal/plugins/gnmplutostats/tests --xunit-file=${CIRCLE_TEST_REPORTS}/gnmplutostats.xml
cd portal/plugins/gnmplutostats/frontend; nvm use 8.1; npm run test

echo ===================================================
echo Running predeploy scripts....
echo ===================================================
cd $BUILDDIR
for dir in `find $BUILDDIR/portal/plugins -maxdepth 1 -mindepth 1 -type d | awk -F '/' '{ print $2 }' | grep -v -E '^\.'`; do echo Trying to run "${PWD}/$dir/pre_deploy.sh"; if [ -x "${PWD}/$dir/pre_deploy.sh" ]; then ${PWD}/$dir/pre_deploy.sh; fi; done
rm -f portal/__init__.py; rm -f portal/plugins/__init__.py
mkdir -p /opt/cantemo/portal/portal/plugins
rm -rf portal/plugins/gnmdownloadablelink/node_modules
cd portal/plugins/gnmplutostats/frontend; nvm use 8.1; npm run build
rm -rf portal/plugins/gnmplutostats/frontend
#
#echo ===================================================
#echo Building common components RPMs....
#echo ===================================================
#cd $BUILDDIR
#rpmbuild -bb portal-codemirror.spec
#./upload_with_hash.sh ~/rpmbuild/RPMS/noarch/portal-codemirror-5.26.0-2.noarch.rpm s3://gnm-multimedia-deployables/gnm_portal_plugins/static/portal-codemirror-5.26.0-2.noarch.rpm
#mkdir -p ~/rpmbuild/BUILD/static
#cp -a static/chartjs ~/rpmbuild/BUILD/static
#rpmbuild -bb portal-chartjs.spec
#./upload_with_hash.sh ~/rpmbuild/RPMS/noarch/portal-chartjs-1.0-1.noarch.rpm s3://gnm-multimedia-deployables/gnm_portal_plugins/static/portal-chartjs-1.0-1.noarch.rpm
#cp -a static/jquery.cookie.js /Users/localhome/rpmbuild/BUILD/static
#rpmbuild -bb portal-jquery-cookie.spec
#./upload_with_hash.sh ~/rpmbuild/RPMS/noarch/portal-jquery-cookie-1.4.1-1.noarch.rpm s3://gnm-multimedia-deployables/gnm_portal_plugins/static/portal-jquery-cookie-1.4.1-1.noarch.rpm
#cp -a static/knockout-3.3.0.js /Users/localhome/rpmbuild/BUILD/static
#rpmbuild -bb portal-knockout.spec
#./upload_with_hash.sh ~/rpmbuild/RPMS/noarch/portal-knockout-3.3.0-1.noarch.rpm s3://gnm-multimedia-deployables/gnm_portal_plugins/static/portal-knockout-3.3.0-1.noarch.rpm
#rpmbuild -bb portal-vkbeautify.spec
#./upload_with_hash.sh ~/rpmbuild/RPMS/noarch/portal-vkbeautify-0.99.0-1.noarch.rpm s3://gnm-multimedia-deployables/gnm_portal_plugins/static/portal-vkbeautify-0.99.0-1.noarch.rpm
#rpmbuild -bb portal-fontawesome.spec
#./upload_with_hash.sh ~/rpmbuild/RPMS/noarch/portal-fontawesome-4.7.0-1.noarch.rpm s3://gnm-multimedia-deployables/gnm_portal_plugins/static/portal-fontawesome-4.7.0-1.noarch.rpm

echo ===================================================
echo Building RPMs....
echo ===================================================
cd $BUILDDIR
bash ./buildrpms.sh
