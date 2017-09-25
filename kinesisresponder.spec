%define name portal-kinesisresponder
%define version 1.0
%define unmangled_version 1.0
%define release 22

Summary: Base plugin to process messages from an Amazon Kinesis stream
Name: %{name}
Version: %{version}
Release: %{release}
License: Internal GNM software
Source0: kinesisresponder.tar.gz
Group: Applications/Productivity
BuildRoot: %{_tmppath}/kinesisresponder
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Andy Gallagher <andy.gallagher@theguardian.com>
Requires: Portal >= 3.0.0

%description
This plugin provides the base functions for reading from a Kinesis stream.  It does not expose any functionality directly,
but is a base that other plugins can use to do useful things with those messages

%prep

%build

%install
mkdir -p $RPM_BUILD_ROOT/opt/cantemo/portal/portal/plugins/kinesisresponder
cd $RPM_BUILD_ROOT/opt/cantemo/portal
tar xvzf %{_sourcedir}/kinesisresponder.tar.gz

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
/opt/cantemo/portal/portal/plugins/kinesisresponder

%post
/opt/cantemo/portal/manage.py migrate kinesisresponder --noinput

%preun
