Name:           sv-lang
Version:        6.0
Release:        1%{?dist}
Summary:        SystemVerilog compiler and language services
License:        MIT

URL:            https://github.com/MikePopoloski/slang
Source0:        https://github.com/MikePopoloski/slang/archive/v%{version}.tar.gz

BuildRequires:  git cmake doxygen
BuildRequires:  python3 python3-devel python3-setuptools
%if ! (0%{?rhel} || 0%{?openEuler} || (0%{?fedora} > 34 && 0%{?fedora} < 37))
BuildRequires:  fmt-devel catch-devel pybind11-devel
%endif
%if 0%{?rhel} == 8
BuildRequires:  gcc-toolset-12-build
BuildRequires:  gcc-toolset-12-binutils
BuildRequires:  gcc-toolset-12-gcc
BuildRequires:  gcc-toolset-12-gcc-c++
BuildRequires:  gcc-toolset-12-annobin-plugin-gcc
%else
BuildRequires:  gcc-c++
%endif

%global __cmake_in_source_build 1

%description
Slang is a software library that provides various components
for lexing, parsing, type checking, and elaborating SystemVerilog code.

%package        devel
Summary:        Development library of %{name}
Requires:       %{name} = %{version}-%{release}

%description    devel
Development files for %{name} library

%package        python
Summary:        Python library of %{name}
Requires:       %{name} = %{version}-%{release}

%description    python
Python bindings for %{name} library

%prep
%autosetup -n slang-%{version}

# python destination
sed -i 's|DESTINATION .)|DESTINATION ${Python_SITEARCH})|' bindings/CMakeLists.txt
# no tests
sed -i '/tests/d' tools/tidy/CMakeLists.txt
# non-existent
sed -i '/span.hpp/d' external/CMakeLists.txt

%build
mkdir -p build
pushd build
%if 0%{?rhel} == 8
%undefine _annotated_build
%{?enable_devtoolset12:%{enable_devtoolset12}}
%endif

%cmake .. -Wno-dev \
       -DCMAKE_SKIP_RPATH=ON \
       -DCMAKE_VERBOSE_MAKEFILE=OFF \
       -DCMAKE_BUILD_TYPE=RelWithDebInfo \
       -DBUILD_SHARED_LIB=ON \
       -DSLANG_LIB_NAME="svlang" \
       -D SLANG_USE_MIMALLOC=OFF \
       -DSLANG_INCLUDE_DOCS=OFF \
       -DSLANG_INCLUDE_TESTS=OFF \
       -DSLANG_INCLUDE_PYLIB=ON \
       -DSLANG_INCLUDE_TOOLS=ON \
       -DSLANG_INCLUDE_INSTALL=ON
%cmake_build
popd

%install
pushd build
%cmake_install
popd
# clean externals
rm -rf %{buildroot}/%{_includedir}/*.*
find %{buildroot}/%{_includedir} -mindepth 1 -maxdepth 1 ! -name 'slang' -type d -not -path '.' -exec rm -rf {} +

%check
export LD_LIBRARY_PATH=%{buildroot}/%{_libdir}:%{_builddir}/%{name}/build/lib
pushd build
make test || true
popd

%files
%license LICENSE
%doc README.md
%{_bindir}/*
%exclude %{_libdir}/cmake/*
%{_libdir}/*


%files devel
%{_includedir}/slang
%{_datadir}/pkgconfig/*
%{_libdir}/cmake/*

%files python
%{python3_sitearch}/*

%changelog
