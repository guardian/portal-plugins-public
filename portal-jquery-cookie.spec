%define name portal-jquery-cookie
%define version 1.4.1
%define unmangled_version 5.26.0
%define release 1

Summary: Provides the Codemirror javascript interface to edit XML files etc.
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
%defattr(-,root,root)
/opt/cantemo/portal/portal_media/js/jquery.cookie.js

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
