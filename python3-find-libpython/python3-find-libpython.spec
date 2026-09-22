%global pypi_name find-libpython
%global oname find_libpython
%global debug_package %{nil}
Name:           python3-%{pypi_name}
Version:        0.5.1
Release:        1%{?dist}
Summary:        Finds the libpython associated with the current environment
License:        MIT
URL:            https://github.com/ktbarrett/find_libpython
Source0:        https://github.com/ktbarrett/find_libpython/archive/v%{version}.tar.gz

BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# 0.5.1 is a PEP 621 project and needs setuptools >= 61.2 to build, but the el9
# repositories only ship setuptools 53 for the default python3.9, so no el9
# chroot can satisfy python3dist(setuptools) >= 61.2.  Build the wheel in an
# isolated environment instead and let it fetch its own backend (the COPR
# project has networking enabled).
BuildRequires:  python3-pip

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

%generate_buildrequires
%pyproject_buildrequires -N

%build
%{python3} -m pip wheel --no-deps --wheel-dir %{_pyproject_wheeldir} .

%install
%pyproject_install
%pyproject_save_files %{oname}

%files -n python3-%{pypi_name} -f %{pyproject_files}
%license LICENSE
%doc README.md
%{_bindir}/*

%changelog
* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 0.5.1-1
- Update to 0.5.1
- Convert from setup.py to pyproject-rpm-macros
- Build the wheel in an isolated environment: el9 only ships setuptools
  53 for python3.9, which cannot build a PEP 621 project, and upstream
  0.5.1 requires setuptools >= 61.2
