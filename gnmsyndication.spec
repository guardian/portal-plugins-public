%define name portal-pluto-gnmsyndication
%define version 2.1
%define unmangled_version 2.1
%define release 3

Summary: GNM Multimedia Publication Dashboard
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmsyndication.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmsyndication
Prefix: %{_prefix}
BuildArch: noarch
Vendor: David Allison <david.allison@theguardian.com> and Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal  portal-chartjs >= 1.0 portal-jquery-cookie >= 1.4.0

%description
Fully featured interface to show what video and audio content is being produced and where it is being sent.

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmsyndication
cp -a /opt/cantemo/portal/portal/plugins/gnmsyndication/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmsyndication

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmsyndication

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmsyndication --noinput

%preun
