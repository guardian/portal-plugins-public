#!/bin/bash

function did_it_work {
    if [ "$?" != "0" ]; then
    echo The script broke!
    exit 1
    fi
}

echo Attempting to copy Portal theme files to the required paths
sudo mkdir -p /opt/cantemo/portal/portal_themes/gnm/templates/media
sudo chown ubuntu /opt/cantemo/portal/portal_themes/gnm/templates/media
sudo cp -a /home/ubuntu/portal-plugins-public/gnmawsgr/portal_theme_files/media_view.html /opt/cantemo/portal/portal_themes/gnm/templates/media/media_view.html
did_it_work
sudo chown ubuntu /opt/cantemo/portal/portal_themes/gnm/templates/media/media_view.html
sudo cp -a /home/ubuntu/portal-plugins-public/gnmawsgr/portal_theme_files/media_inc_preview.html /opt/cantemo/portal/portal_themes/gnm/templates/media/media_inc_preview.html
did_it_work
sudo chown ubuntu /opt/cantemo/portal/portal_themes/gnm/templates/media/media_inc_preview.html
sudo mkdir -p /opt/cantemo/portal/portal_media/gnm/css
sudo chown ubuntu /opt/cantemo/portal/portal_media/gnm/css
sudo cp -a /home/ubuntu/portal-plugins-public/gnmawsgr/portal_theme_files/logos.css /opt/cantemo/portal/portal_media/gnm/css/logos.css
did_it_work
sudo chown ubuntu /opt/cantemo/portal/portal_media/gnm/css/logos.css
sudo mkdir -p /opt/cantemo/portal/portal_media/img/gnm/logos
sudo chown ubuntu /opt/cantemo/portal/portal_media/img/gnm/logos
sudo cp -a /home/ubuntu/portal-plugins-public/gnmawsgr/portal_theme_files/axe.gif /opt/cantemo/portal/portal_media/img/gnm/logos/axe.gif
did_it_work
sudo chown ubuntu /opt/cantemo/portal/portal_media/img/gnm/logos/axe.gif
sudo cp -a /home/ubuntu/portal-plugins-public/gnmawsgr/portal_theme_files/archived.png /opt/cantemo/portal/portal_media/img/gnm/logos/archived.png
did_it_work
sudo chown ubuntu /opt/cantemo/portal/portal_media/img/gnm/logos/archived.png
sudo cp -a /home/ubuntu/portal-plugins-public/gnmawsgr/portal_theme_files/restored.png /opt/cantemo/portal/portal_media/img/gnm/logos/restored.png
did_it_work
sudo chown ubuntu /opt/cantemo/portal/portal_media/img/gnm/logos/restored.png
sudo cp -a /home/ubuntu/portal-plugins-public/gnmawsgr/portal_theme_files/delete.png /opt/cantemo/portal/portal_media/delete.png
did_it_work
sudo chown ubuntu /opt/cantemo/portal/portal_media/delete.png
echo The script completed with no copying errors