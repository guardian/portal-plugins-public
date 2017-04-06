%define name portal-pluto-gnmpagerduty
%define version 1.0
%define unmangled_version 1.0
%define release 1

Summary: Pluto PagerDuty plugin
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmpagerduty.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmpagerduty
Prefix: %{_prefix}
BuildArch: noarch
Vendor: David Allison <david.allison@theguardian.com> and Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal pluto portal_gnm_vidispine

%description
A Portal plugin that allows alerts to be sent to PagerDuty when storages get too full.

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmpagerduty
cp -a /opt/cantemo/portal/portal/plugins/gnmpagerduty/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmpagerduty

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmpagerduty

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmpagerduty --noinput
/opt/cantemo/portal/manage.py install_pagerduty

%preun
