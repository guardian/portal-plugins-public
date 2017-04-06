%define name portal-pluto-gnmyoutube
%define version 1.0
%define unmangled_version 1.0
%define release 4

Summary: Sentry javascript integration
Name: %{name}
Version: %{version}
Release: %{release}
License: GPL
Source0: ravenjs.tar.gz
Group: Applications/Productivity
BuildRoot: %{_tmppath}/ravenjs
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal

%description
Allows catching of Javascript exceptions from Portal in Sentry

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/ravenjs
cp -a /opt/cantemo/portal/portal/plugins/ravenjs/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/ravenjs

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/ravenjs

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
echo RavenJS has been installed.  Now, you need to update your settings to contain RAVEN_DSN={'public_dsn': '{your_public_dsn_here}'}
