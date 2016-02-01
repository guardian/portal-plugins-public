%define name portal-plutostats
%define version 1.0
%define unmangled_version 1.0
%define release 8

#%signature gpg
#%_gpg_name Andy Gallagher <andy.gallagher@theguardian.com>
#%_gpgpath /usr
#%_gpgbin /usr/bin/gpg

Summary: Simple statistics plugin for Pluto. Lives in the Admin interface.
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmplutostats.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmpurgemeister
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal

%description
Simple statistics plugin that shows pie charts of the status of commissions, projects and masters in an Admin panel.

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmplutostats
cp -a /opt/cantemo/portal/portal/plugins/gnmplutostats/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmplutostats

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmplutostats

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
