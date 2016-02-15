%define name portal-pluto-gnmpropgagation
%define version 2.0
%define unmangled_version 2.0
%define release 2

Summary: Pluto flag propagator plugin
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmpropagation.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmsyndication
Prefix: %{_prefix}
BuildArch: noarch
Vendor: David Allison <david.allison@theguardian.com> and Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal pluto portal_gnm_vidispine

%description
Businesslogic rule enabled plugin to propagate flag values down commissions and items

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmpropagation
cp -a /opt/cantemo/portal/portal/plugins/gnmpropagation/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmpropagation
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnm_businesslogic/logic
cp /opt/cantemo/portal/portal/plugins/gnm_businesslogic/logic/tickbox_propagation.xml $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnm_businesslogic/logic

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmpropagation
/opt/cantemo/portal/portal/plugins/gnm_businesslogic/logic/tickbox_propagation.xml

%post
/opt/cantemo/portal/manage.py synchronize_businesslogic

%preun
