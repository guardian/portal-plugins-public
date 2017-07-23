%define name portal-jquery-cookie
%define version 1.4.1
%define unmangled_version 1.4.1
%define release 1

Summary: Jquery cookie handling functions
Name: %{name}
Version: %{version}
Release: %{release}
License: MIT
Source0: codemirror.zip
Group: Applications/Productivity
BuildRoot: %{_tmppath}/portal-codemirror
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Klaus Hartl
Requires: Portal

%description
Jquery cookie handling functions

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/
cp -a static/jquery.cookie.js $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js

%clean

%files
%defattr(644,root,root,755)
/opt/cantemo/portal/portal_media/js/jquery.cookie.js

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
