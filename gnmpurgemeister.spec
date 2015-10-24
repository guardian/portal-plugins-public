%define name portal-purgemeister
%define version 1.0
%define unmangled_version 1.0
%define release 1

Summary: An autopurger plugin for Cantemo Portal
Name: %{name}
Version: %{version}
Release: %{release}
License: UNKNOWN
Source0: gnmpurgemeister.tar.gz
Group: Development/Libraries
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmpurgemeister
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal

%description
UNKNOWN

%prep
#%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmpurgemeister
cp -a /opt/cantemo/portal/portal/plugins/gnmpurgemeister/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmpurgemeister

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmpurgemeister

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmpurgemeister --noinput