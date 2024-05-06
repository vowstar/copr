%global pypi_name cocotb-test
%global debug_package %{nil}
Name:           python3-%{pypi_name}
Version:        0.2.5
Release:        1%{?dist}
Summary:        Provides standard python unit testing capabilities for cocotb
License:        BSD-2-Clause
URL:            https://github.com/themperek/cocotb-test
Source0:        https://github.com/themperek/cocotb-test/archive/v%{version}.tar.gz

BuildRequires:  git gcc-c++ make python3-devel python3-setuptools
Requires:       python3dist(cocotb)

BuildArch:      noarch

%{?python_provide:%python_provide python3-%{pypi_name}}

%description
cocotb-test provides standard python unit testing capabilities for cocotb
allow the look and feel of Python unit testing
remove the need for Makefiles (includes Makefile compatibility mode)
allow easy customization of simulation flow
allow to use pytest-xdist or pytest-parallel for parallel runs

%package -n %{pypi_name}
Summary:        %{summary}
%description -n %{pypi_name}
cocotb-test provides standard python unit testing capabilities for cocotb
allow the look and feel of Python unit testing
remove the need for Makefiles (includes Makefile compatibility mode)
allow easy customization of simulation flow
allow to use pytest-xdist or pytest-parallel for parallel runs
Provides:       %{pypi_name}

%prep
%autosetup -n %{pypi_name}-%{version}

%build
%py3_build

%install
%py3_install

%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{_bindir}/*
%{python3_sitelib}/*

%changelog
