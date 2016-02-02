%define name portal-pluto-gnmawsgr
%define version 1.0
%define unmangled_version 1.0
%define release 1

Summary: GNM Amazon Web Services Glacier Restore
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmawsgr.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmawsgr
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Dave Allison <david.allison@theguardian.com> and Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal pluto

%description
Allows restoration of items and collections from the Amazon Web Services Glacier system.

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmawsgr
cp -a /opt/cantemo/portal/portal/plugins/gnmawsgr/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmawsgr

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmawsgr

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmawsgr --noinput

%preun
