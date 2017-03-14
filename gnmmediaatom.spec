%define name portal-pluto-gnmmediaatom
%define version 1.0
%define unmangled_version 1.0
%define release 4

Summary: Media Atom integration plugin
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmmediaatom.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmmediaatom
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Editorial Tools <digitalcms.dev@theguardian.com>
Requires: Portal pluto

%description
Plugin for media atom support

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmmediaatom
cp -a /opt/cantemo/portal/portal/plugins/gnmmediaatom/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmmediaatom

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmmediaatom

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmmediaatom --noinput

%preun
