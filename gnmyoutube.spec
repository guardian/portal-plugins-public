%define name portal-plutoyoutube
%define version 1.0
%define unmangled_version 1.0
%define release 1

#%signature gpg
#%_gpg_name Andy Gallagher <andy.gallagher@theguardian.com>
#%_gpgpath /usr
#%_gpgbin /usr/bin/gpg

Summary: Youtube connector for Pluto to allow for the automatic updating of categories
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmyoutube.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmyoutube
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal

%description
Youtube connector for Pluto to allow for the automatic updating of categories.

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmyoutube
cp -a /opt/cantemo/portal/portal/plugins/gnmyoutube/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmyoutube

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmyoutube

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmyoutube

%preun
