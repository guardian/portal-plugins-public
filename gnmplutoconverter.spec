%define name portal-plutoconverter
%define version 1.0
%define unmangled_version 1.0
%define release 5

Summary: Gearbox plugin to convert general media items into Pluto masters
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmplutoconverter.tar.gz
Group: Applications/Productivity
BuildRoot: %{_tmppath}/gnmplutoconverter
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com> and Dave Allison <david.allison@theguardian.com>
Requires: Portal

%description
Allows any user with write access to adjust the metadata on any media item to turn it into a master, and associate with
a given commission and project.

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmplutoconverter
cp -a /opt/cantemo/portal/portal/plugins/gnmplutoconverter/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmplutoconverter

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmplutoconverter

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
