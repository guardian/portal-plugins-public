%define name portal-chartjs
%define version 1.0
%define unmangled_version 1.0
%define release 1

Summary: Provides the ChartJS javascript interface to generate graphs. Actual version is unknown.
Name: %{name}
Version: %{version}
Release: %{release}
License: MIT
Source0: chartjs.zip
Group: Applications/Productivity
BuildRoot: %{_tmppath}/portal-codemirror
Prefix: %{_prefix}
BuildArch: noarch
Vendor: DevExpress
Requires: Portal

%description
The ChartJS graphing widgets for javascript

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/
cp -a static/chartjs $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js

%clean

%files
%defattr(644,root,root,755)
/opt/cantemo/portal/portal_media/js/chartjs

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
