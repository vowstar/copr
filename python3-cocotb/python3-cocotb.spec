%global pypi_name cocotb
Name:           python3-%{pypi_name}
Version:        1.9.0
Release:        1%{?dist}
Summary:        Coroutine based cosimulation library for writing VHDL and Verilog
License:        BSD
URL:            https://cocotb.org
Source0:        https://github.com/cocotb/cocotb/archive/v%{version}.tar.gz

BuildRequires:  git gcc-c++ make python3-devel python3-setuptools libstdc++-static
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

%build
#sed -i '/-rpath/d' cocotb_build_libs.py
sed -i 's|"-static-libstdc++"||g' cocotb_build_libs.py
sed -i 's|echo "acc.*|echo "acc+=rw,wn,cbk:*" > $@|g' cocotb/share/makefiles/simulators/Makefile.vcs
sed -i 's|+acc+1|-debug_access+all -debug_region+cell+encrypt -debug_region+cell+lib|g' cocotb/share/makefiles/simulators/Makefile.vcs
sed -i 's|-debug -load|-load|g' cocotb/share/makefiles/simulators/Makefile.vcs

%py3_build


%install
%py3_install


%files -n python3-%{pypi_name}
%license LICENSE
%doc README.md
%{_bindir}/*
%{python3_sitearch}/*

%changelog
