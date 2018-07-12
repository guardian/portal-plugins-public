%define name portal-pluto-gnmdownloadablelink
%define version 1.0
%define unmangled_version 1.0
%define release 20

Summary: Simple sharing of media by creating a publically available link
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmatomresponder.tar.gz
Group: Applications/Productivity
BuildRoot: %{_tmppath}/gnmdownloadablelink
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal >= 3.0.0 pluto >= 3.0-697 gnmvidispine-portal >= 1.9-83 portal-fontawesome >= 4.7.0-1

%description
Simple sharing of media by creating a publically available link

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmdownloadablelink
cd $RPM_BUILD_ROOT/opt/cantemo/portal
tar xvzf %{_sourcedir}/gnmdownloadablelink.tar.gz
rm -rf $RPM_BUILD_ROOT/opt/cantemo/portal/gnmdownloadablelink/node_modules

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmdownloadablelink

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmdownloadablelink --noinput

%preun
