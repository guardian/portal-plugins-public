%define name portal-gnmlogsearch
%define version 1.0
%define unmangled_version 1.0
%define release 6

#%signature gpg
#%_gpg_name Andy Gallagher <andy.gallagher@theguardian.com>
#%_gpgpath /usr
#%_gpgbin /usr/bin/gpg

Summary: Plugin to provide detailed log views from Vidispine
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmlogsearch.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmlogsearch
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com> and David Allison <david.allison@theguardian.com>
Requires: Portal

%description
Portal plugin to show highly detailed debugging information from Vidispine about jobs in progress and completed

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmlogsearch
cp -a /opt/cantemo/portal/portal/plugins/gnmlogsearch/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmlogsearch

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmlogsearch

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
