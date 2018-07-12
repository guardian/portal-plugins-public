%define name portal-fontawesome
%define version 4.7.0
%define unmangled_version 4.7.0
%define release 1

Summary: The font-awesome toolkit, packaged for Cantemo Portal
Name: %{name}
Version: %{version}
Release: %{release}
License: MIT
Source0: font-awesome-4.7.0.zip
Group: Applications/Productivity
BuildRoot: %{_tmppath}/portal-codemirror
Prefix: %{_prefix}
BuildArch: noarch
Vendor: DevExpress
Requires: Portal

%description
The font-awesome toolkit, packaged for Cantemo Portal

%prep

%build

%install
curl https://fontawesome.com/v4.7.0/assets/font-awesome-4.7.0.zip > /tmp/font-awesome.zip

mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/
cd $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/
unzip /tmp/font-awesome.zip

%clean
rm -f /tmp/font-awesome.zip

%files
%defattr(644,root,root,755)
/opt/cantemo/portal/portal_media/font-awesome-4.7.0

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
