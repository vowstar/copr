%global pypi_name cocotb
Name:           python3-%{pypi_name}
Version:        2.1.0
Release:        1%{?dist}
Summary:        Coroutine based cosimulation library for writing VHDL and Verilog
License:        BSD-3-Clause
URL:            https://cocotb.org
Source0:        https://files.pythonhosted.org/packages/source/c/cocotb/cocotb-%{version}.tar.gz

BuildRequires:  gcc-c++ make python3-devel python3-setuptools libstdc++-static
# runtime dependencies of cocotb 2.x, see pyproject.toml:
#  - find-libpython: cocotb-config --libpython / the Makefile flow
#  - pytest: the cocotb pytest plugin and test runner
#  - exceptiongroup: imported on python < 3.11, i.e. on every EL chroot
Requires:       python3dist(find-libpython)
Requires:       python3dist(exceptiongroup)
Requires:       python3dist(pytest) >= 6

%description
Cocotb is a coroutine based cosimulation library
for writing VHDL and Verilog testbenches in Python.

%{?python_provide:%python_provide python3-%{name}}

%package -n     cocotb
Summary:       %{summary}
%description -n cocotb
cocotb is a coroutine based cosimulation library for writing VHDL
and Verilog testbenches in Python.
Provides:       cocotb

%prep
%autosetup -n %{pypi_name}-%{version}
# cocotb 2.x describes its metadata in pyproject.toml ([project], PEP 621) and
# consumes it with setuptools-git-versioning, which needs setuptools >= 77.
# EL8/EL9 ship much older setuptools (53 on EL9) that ignore the [project]
# table completely, so hand name/version/entry points to setup() the classic way.
%{__sed} -i 's|^    ext_modules=get_ext(),$|    name="%{pypi_name}",\n    version="%{version}",\n    entry_points={"console_scripts": ["cocotb-config = cocotb_tools.config:main"]},\n    ext_modules=get_ext(),|' setup.py
%{__grep} -q 'version="%{version}"' setup.py
%{__grep} -q 'cocotb-config = cocotb_tools.config:main' setup.py

%build
sed -i 's|"-static-libstdc++"||g' cocotb_build_libs.py
%py3_build


%install
%py3_install


%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{_bindir}/*
%{python3_sitearch}/*

%changelog
