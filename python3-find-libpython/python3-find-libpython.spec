%global pypi_name find-libpython
%global oname find_libpython
%global debug_package %{nil}
Name:           python3-%{pypi_name}
Version:        0.4.0
Release:        1%{?dist}
Summary:        Finds the libpython associated with the current environment
License:        MIT
URL:            https://github.com/ktbarrett/find_libpython
Source0:        https://github.com/ktbarrett/find_libpython/archive/v%{version}.tar.gz

BuildRequires:  git gcc-c++ make python3-devel python3-setuptools

BuildArch:      noarch

%{?python_provide:%python_provide python3-%{pypi_name}}

%description
A pypi project version of this gist, which also appears within the PyCall
library.
The library is designed to find the path to the libpython dynamic library for
the current Python environment. It should work with many types of installations,
whether it be conda-managed, system-managed, or otherwise. And it should
function on Windows, Mac OS/OS X, and any Linux distribution.
This code is useful in several contexts, including projects that embed a Python
interpreter into another process, or Python library build systems.

%package -n %{pypi_name}
Summary:        %{summary}
%description -n %{pypi_name}
A pypi project version of this gist, which also appears within the PyCall
library.
The library is designed to find the path to the libpython dynamic library for
the current Python environment. It should work with many types of installations,
whether it be conda-managed, system-managed, or otherwise. And it should
function on Windows, Mac OS/OS X, and any Linux distribution.
This code is useful in several contexts, including projects that embed a Python
interpreter into another process, or Python library build systems.
Provides:       %{pypi_name}

%prep
%autosetup -n %{oname}-%{version}

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
