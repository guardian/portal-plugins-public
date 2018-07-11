%define name portal-codemirror
%define version 5.26.0
%define unmangled_version 5.26.0
%define release 2

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
The Codemirror javascript widget, packaged for Cantemo Portal

%prep

%build
curl https://codeload.github.com/codemirror/CodeMirror/zip/%{version} > /tmp/codemirror.zip
unzip /tmp/codemirror.zip
rm -f /tmp/codemirror.zip

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/
cd CodeMirror-%{version}
npm install
npm run build
rm -rf node_modules
rm -f .gitattributes .gitignore .npmignore .travis.yml
cd ..
cp -a CodeMirror-%{version} $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/codemirror

%clean
rm -rf CodeMirror-%{version}

%files
%defattr(644,root,root,755)
/opt/cantemo/portal/portal_media/js/codemirror

%post
/opt/cantemo/portal/manage.py collectstatic --noinput

%preun
