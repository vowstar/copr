Name:           sv-lang
Version:        7.0
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

%if ! (0%{?fedora})
# python3.6 support
sed -i -e 's/GIT_TAG.*/GIT_TAG v2.12.0/' bindings/CMakeLists.txt
%endif

# python3.13 support
sed -i '/r = _PyLong_AsByteArray/{N;d;}' bindings/python/NumericBindings.cpp
sed -i '/if (r == -1)/i\    int r = -1;\n#if PY_VERSION_HEX < 0x030D0000\n    r = _PyLong_AsByteArray(reinterpret_cast<PyLongObject*>(value.ptr()),\n                            reinterpret_cast<unsigned char*>(mem.data()), numBytes, 1, 1);\n#else\n    // fix build error with python 3.13\n    r = _PyLong_AsByteArray(reinterpret_cast<PyLongObject*>(value.ptr()),\n                            reinterpret_cast<unsigned char*>(mem.data()), numBytes, 1, 1, 0);\n    // No exception is thrown here because it will be done later.\n#endif' bindings/python/NumericBindings.cpp


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
       -DSLANG_USE_MIMALLOC=OFF \
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
* Sun Jun 19 2022 Cristian Balint <cristian.balint@gmail.com>
- github update releases
