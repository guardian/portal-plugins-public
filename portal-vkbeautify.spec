%define name portal-vkbeautify
%define version 0.99.0
%define unmangled_version 0.99.0
%define release 1

Summary: Provides the vkBeautifier javascript library to handle XML client-side
Name: %{name}
Version: %{version}
Release: %{release}
License: MIT
Source0: vkbeautify.zip
Group: Applications/Productivity
BuildRoot: %{_tmppath}/portal-codemirror
Prefix: %{_prefix}
BuildArch: noarch
Vendor: http://www.eslinstructor.net/vkbeautify/
Requires: Portal

%description
vkBeautify javascript plugin, packaged for Cantemo Portal

%prep

%build
npm install uglify-js -g
curl https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/vkbeautify/vkbeautify.0.99.00.beta.js > /tmp/vkbeautify.js
echo $PWD
uglifyjs /tmp/vkbeautify.js --compress --mangle -o /tmp/vkbeautify.min.js

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/
mv /tmp/vkbeautify.min.js $RPM_BUILD_ROOT/opt/cantemo/portal/portal_media/js/

%clean
rm -f /tmp/vkbeautify.js /tmp/vkbeautify.min.js

%files
%defattr(644,root,root,755)
/opt/cantemo/portal/portal_media/js/vkbeautify.min.js

%post

%preun
