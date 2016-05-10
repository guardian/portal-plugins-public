%define name portal-pluto-gnmuploadprofiler
%define version 1.0
%define unmangled_version 1.0
%define release 3

Summary: GNM Upload Speed Profiler
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: gnmuploadprofiler.tar.gz
Group: Applications/Productivity
#BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRoot: %{_tmppath}/gnmuploadprofiler
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal pluto portal_gnm_vidispine

%description
Plugin to capture timings for the upload process of GNM videos

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmuploadprofiler
cp -a /opt/cantemo/portal/portal/plugins/gnmuploadprofiler/* $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmuploadprofiler
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnm_businesslogic/logic
cp $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnmuploadprofiler/businesslogic/mdtrigger_upload_profiler.xml $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/gnm_businesslogic/logic

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/gnmuploadprofiler
/opt/cantemo/portal/portal/plugins/gnm_businesslogic/logic/mdtrigger_upload_profiler.xml

%post
/opt/cantemo/portal/manage.py migrate gnmuploadprofiler --noinput
/opt/cantemo/portal/manage.py collectstatic --noinput
/opt/cantemo/portal/manage.py synchronize_businesslogic
patch /opt/cantemo/python/lib/python2.6/site-packages/django/db/backends/postgresql_psycopg2/operations.py < /opt/cantemo/portal/portal/plugins/gnmuploadprofiler/operations_django_patch.diff
%preun
