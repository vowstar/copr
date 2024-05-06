%global pypi_name cocotb
Name:           python3-%{pypi_name}
Version:        1.8.1
Release:        1%{?dist}
Summary:        Coroutine based cosimulation library for writing VHDL and Verilog
License:        BSD
URL:            https://cocotb.org
Source0:        https://github.com/cocotb/cocotb/archive/v%{version}.tar.gz

Patch1: 0001-Fix-vcs-compile-options-and-pli.tab.patch

BuildRequires:  git gcc-c++ make python3-devel python3-setuptools
Requires:       python3dist(setuptools)
Requires:       python3dist(pytest)

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

pushd %{pypi_name}-%{version}
%patch -P 1 -p1
popd

%build
#sed -i '/-rpath/d' cocotb_build_libs.py
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
