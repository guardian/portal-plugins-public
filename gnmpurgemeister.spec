%define name portal-purgemeister
%define version 1.2
%define unmangled_version 1.2
%define release 4

#%signature gpg
#%_gpg_name Andy Gallagher <andy.gallagher@theguardian.com>
#%_gpgpath /usr
#%_gpgbin /usr/bin/gpg

Summary: An autopurger plugin for Cantemo Portal
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmpurgemeister.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmpurgemeister
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal

%description
Plugin for Cantemo Portal that allows files older than a certain age, and matching certain metadata specifications,
to be removed from the system and deleted from disk.

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
/opt/cantemo/portal/manage.py install_purgemeister

%preun
/opt/cantemo/portal/manage.py uninstall_purgemeister
