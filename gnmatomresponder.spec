%define name portal-pluto-gnmatomresponder
%define version 1.0
%define unmangled_version 1.0
%define release 20

Summary: Integration to ingest media that has been sent to the media atom tool
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmatomresponder.tar.gz
Group: Applications/Productivity
BuildRoot: %{_tmppath}/gnmatomresponder
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal >= 3.0.0 pluto >= 3.0 portal-kinesisresponder >= 1.0 gnmvidispine-portal >= 1.9

%description
Plugin for Pluto that allows creation of masters from media that was sent to the media atom tool

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmatomresponder
cd $RPM_BUILD_ROOT/opt/cantemo/portal
tar xvzf %{_sourcedir}/gnmatomresponder.tar.gz

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmatomresponder

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmatomresponder --noinput

%preun
