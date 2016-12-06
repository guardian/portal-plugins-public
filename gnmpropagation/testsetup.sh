#!/bin/bash

#this script is run from circle.yml when setting up for a CI build
BL_DEPLOY_PATH=/opt/cantemo/portal/portal/plugins/gnm_businesslogic/logic
sudo mkdir -p ${BL_DEPLOY_PATH}
sudo chown ubuntu ${BL_DEPLOY_PATH}

for x in `ls gnmpropagation/businesslogic/*.xml`; do
    echo      Symlinking $x to "${BL_DEPLOY_PATH}"
    ln -s $x "${BL_DEPLOY_PATH}"
done
