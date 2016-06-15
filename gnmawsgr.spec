%define name portal-pluto-gnmawsgr
%define version 1.2
%define unmangled_version 1.2
%define release 2

Summary: GNM Amazon Web Services Glacier Restore
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmawsgr.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmawsgr
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Dave Allison <david.allison@theguardian.com> and Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal pluto portal_gnm_vidispine

%description
Allows restoration of items and collections from the Amazon Web Services Glacier system.

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmawsgr
cp -a /opt/cantemo/portal/portal/plugins/gnmawsgr/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmawsgr
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/gnmawsgr/gnm/templates/media
cp -a /opt/cantemo/portal/portal_themes/gnm/templates/media/media_view.html $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/gnmawsgr/gnm/templates/media/media_view.html
cp -a /opt/cantemo/portal/portal_themes/gnm/templates/media/media_inc_preview.html $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/gnmawsgr/gnm/templates/media/media_inc_preview.html
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/gnmawsgr/gnm/css
cp -a /opt/cantemo/portal/portal_media/gnm/css/logos.css $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/gnmawsgr/gnm/css/logos.css
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/img/gnm/logos
cp -a /opt/cantemo/portal/portal_media/img/gnm/logos/axe.gif $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/img/gnm/logos/axe.gif
cp -a /opt/cantemo/portal/portal_media/img/gnm/logos/archived.png $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/img/gnm/logos/archived.png
cp -a /opt/cantemo/portal/portal_media/img/gnm/logos/restored.png $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/img/gnm/logos/restored.png
cp -a /opt/cantemo/portal/portal_media/delete.png $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/delete.png

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmawsgr
/opt/cantemo/portal/portal_media/img/gnm/logos/axe.gif
/opt/cantemo/portal/portal_media/img/gnm/logos/archived.png
/opt/cantemo/portal/portal_media/img/gnm/logos/restored.png
/opt/cantemo/portal/portal_media/gnmawsgr/gnm/css/logos.css
/opt/cantemo/portal/portal_media/gnmawsgr/gnm/templates/media/media_view.html
/opt/cantemo/portal/portal_media/gnmawsgr/gnm/templates/media/media_inc_preview.html
/opt/cantemo/portal/portal_media/delete.png

%pre
if [ -f /opt/cantemo/portal/portal_media/gnm/css/logos.css ]; then
    mv /opt/cantemo/portal/portal_media/gnm/css/logos.css /opt/cantemo/portal/portal_media/gnm/css/logos_old.css
fi
if [ -f /opt/cantemo/portal/portal_themes/gnm/templates/media/media_view.html ]; then
    mv /opt/cantemo/portal/portal_themes/gnm/templates/media/media_view.html /opt/cantemo/portal/portal_themes/gnm/templates/media/media_view_old.html
fi
if [ -f /opt/cantemo/portal/portal_themes/gnm/templates/media/media_inc_preview.html ]; then
    mv /opt/cantemo/portal/portal_themes/gnm/templates/media/media_inc_preview.html /opt/cantemo/portal/portal_themes/gnm/templates/media/media_inc_preview_old.html
fi

%post
ln -s /opt/cantemo/portal/portal_media/gnmawsgr/gnm/css/logos.css /opt/cantemo/portal/portal_media/gnm/css/logos.css
ln -s /opt/cantemo/portal/portal_media/gnmawsgr/gnm/templates/media/media_view.html /opt/cantemo/portal/portal_themes/gnm/templates/media/media_view.html
ln -s /opt/cantemo/portal/portal_media/gnmawsgr/gnm/templates/media/media_inc_preview.html /opt/cantemo/portal/portal_themes/gnm/templates/media/media_inc_preview.html

/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmawsgr --noinput
/opt/cantemo/portal/manage.py install_glacierrestore
chmod 0775 /opt/cantemo/portal/portal_themes/gnm/templates/media/media_view.html
chmod 0775 /opt/cantemo/portal/portal_themes/gnm/templates/media/media_inc_preview.html
chmod 0775 /opt/cantemo/portal/portal_media/gnm/css/logos.css
chmod 0775 /opt/cantemo/portal/portal_media/img/gnm/logos/axe.gif
chmod 0775 /opt/cantemo/portal/portal_media/img/gnm/logos/archived.png
chmod 0775 /opt/cantemo/portal/portal_media/img/gnm/logos/restored.png
chmod 0775 /opt/cantemo/portal/portal_media/delete.png
 
%preun
