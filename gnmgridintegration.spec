%define name portal-gnmgridintegration
%define version 1.0
%define unmangled_version 1.0
%define release 6

Summary: Integration to allow image snapshots to be directly sent to The Grid
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmgridintegration.tar.gz
Group: Applications/Productivity
BuildRoot: %{_tmppath}/gnmgridintegration
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal portal_gnm_vidispine>=1.0-2

%description
Plugin for Cantemo Portal that allows snapshots taken with the camera icon function to be directly sent on to The Grid

%prep
#%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmgridintegration
cp -a /opt/cantemo/portal/portal/plugins/gnmgridintegration/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmgridintegration

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmgridintegration

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmgridintegration --noinput
echo "Now you must run /opt/cantemo/portal/manage.py install_gridintegration --key {your_key} where {your_key} is a working API key for The Grid"

%preun
/opt/cantemo/portal/manage.py uninstall_gridintegration