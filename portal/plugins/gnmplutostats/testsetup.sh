#!/bin/bash --login
echo Installing javascript testing prereqs
cd portal/plugins/gnmplutostats/frontend
nvm use 8.1 && yarn install