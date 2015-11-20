Name:      networking_plumgrid
Version:   XXX
Release:   1.0
Summary:   PLUMgrid OpenStack Neutron driver

Group:     Applications/System
License:   ASL 2.0
URL:       https://pypi.python.org/pypi/%{name}
Source0:   %{name}-%{version}.tar.gz

BuildArch: noarch
BuildRoot: ~/rpmbuild

%description
This package provides PLUMgrid networking driver for OpenStack Neutron

%prep
%setup -q

%clean
rm -rf %{buildroot}
