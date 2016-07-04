%define name portal-gnmsearchplugin
%define version 0.93
%define unmangled_version 0.93
%define release 3

Summary: Vidispine-specific simplified search plugin, with eye-candy
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmsupasearch.tar.gz
Group: Applications/Productivity
BuildRoot: %{_tmppath}/gnmgridintegration
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal portal_gnm_vidispine>=1.0-2

%description
Plugin for Cantemo Portal that provides an alternative search interface, talking directly to Vidispine.
Also supports 'eye candy' of graphs and word-clouds to help filter down results.

%prep
#%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmsupasearch
cp -a /opt/cantemo/portal/portal/plugins/gnmsupasearch/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmsupasearch

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmsupasearch

%post
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py migrate gnmsupasearch --noinput

%preun
