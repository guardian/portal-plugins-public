%define name portal-codemirror
%define version 5.26.0
%define unmangled_version 5.26.0
%define release 1

Summary: Provides the Codemirror javascript interface to edit XML files etc.
Name: %{name}
Version: %{version}
Release: %{release}
License: MIT
Source0: codemirror.zip
Group: Applications/Productivity
BuildRoot: %{_tmppath}/portal-codemirror
Prefix: %{_prefix}
BuildArch: noarch
Vendor: https://codemirror.net/
Requires: Portal

%description
The Codemirror javascript widget,

%prep

%build
curl https://codeload.github.com/codemirror/CodeMirror/zip/5.26.0 > /tmp/codemirror.zip
unzip /tmp/codemirror.zip
rm -f /tmp/codemirror.zip

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/
cp -a CodeMirror-5.26.0 $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/codemirror

%clean
rm -rf CodeMirror-5.26.0

%files
%defattr(644,root,root,755)
/opt/cantemo/portal/portal_media/js/codemirror

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
