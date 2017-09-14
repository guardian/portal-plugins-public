%define name portal-pluto-gnmyoutube
%define version 1.0
%define unmangled_version 1.0
%define release 5

Summary: GNM Youtube Pluto integration plugin
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
Vendor: David Allison <david.allison@theguardian.com> and Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal

%description
Plugin that collects utilities to support Youtube. Current functionality: update of category IDs

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
/opt/cantemo/portal/manage.py migrate gnmyoutube --noinput

%preun
