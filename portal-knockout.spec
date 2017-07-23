%define name portal-knockout
%define version 3.3.0
%define unmangled_version 3.3.0
%define release 1

Summary: Provides the Knockout javascript library
Name: %{name}
Version: %{version}
Release: %{release}
License: MIT
Source0: codemirror.zip
Group: Applications/Productivity
BuildRoot: %{_tmppath}/portal-knockout
Prefix: %{_prefix}
BuildArch: noarch
Vendor: http://knockoutjs.com/
Requires: Portal

%description
Jquery cookie handling functions

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/
cp -a static/knockout-3.3.0.js $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js

%clean

%files
%defattr(644,root,root,755)
/opt/cantemo/portal/portal_media/js/knockout-3.3.0.js

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
