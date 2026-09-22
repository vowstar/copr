%global pkgvers 0
%global scdate0 20260921
%global schash0 24cec094bcc1401b7d92765ea157ac48bf08fdfe
%global branch0 master
%global source0 https://github.com/berkeley-abc/abc.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           abc
Version:        1.02
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        Sequential logic synthesis and formal verification
License:        MIT
URL:            http://www.eecs.berkeley.edu/~alanmi/abc/abc.htm

# Man page created by Jerry James using upstream text; hence, it is covered by
# the same copyright and license as the code.
Source1:        %{name}.1

# Fedora-specific patch: do not use the bundled libraries
Patch0:         %{name}-bundlelib.patch
# Fedora-specific patch: build a shared library instead of a static library
Patch1:         %{name}-sharedlib.patch
# Fix a minor header issue
Patch2:         %{name}-header.patch
# Set an soname on the library
Patch3:         %{name}-build.patch
# Fix sprintf calls that can overflow their buffers
Patch4:         %{name}-format.patch

Patch100:       %{name}-gcc11.patch

BuildRequires:  git cmake gcc-c++ bzip2-devel readline-devel zlib-devel

Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

Obsoletes:      yosyshq-abc

%global __cmake_in_source_build 1
# Patches are rebased onto the pinned git snapshot and expected to apply exactly;
# keep fuzz at 0 so any future drift fails loudly instead of applying in the
# wrong place (the previous fuzz=100 silently misapplied one CMakeLists hunk).
%global _default_patch_fuzz 0

%description
ABC is a growing software system for synthesis and verification of
binary sequential logic circuits appearing in synchronous hardware
designs.  ABC combines scalable logic optimization based on And-Inverter
Graphs (AIGs), optimal-delay DAG-based technology mapping for look-up
tables and standard cells, and innovative algorithms for sequential
synthesis and verification.

ABC provides an experimental implementation of these algorithms and a
programming environment for building similar applications.  Future
development will focus on improving the algorithms and making most of
the packages stand-alone.  This will allow the user to customize ABC for
their needs as if it were a toolbox rather than a complete tool.

%package        libs
Summary:        Library for sequential synthesis and verification
# ABC includes a bundled and modified version of CUDD 2.4.2, which is
# incompatible with the Fedora-provided CUDD 3.0.0.
Provides:       bundled(cudd) = 2.4.2
Obsoletes:      yosyshq-abc-libs

%description    libs
This package contains the core functionality of ABC as a shared library.

%package        devel
Summary:        Headers and libraries for developing with ABC
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}
Obsoletes:      yosyshq-abc-devel

%description    devel
Headers and libraries for developing applications that use ABC.


%prep
%setup -T -c -n %{name}
git clone --depth 1 -n -b %{branch0} %{source0} .
git fetch --depth 1 origin %{schash0}
git reset --hard %{schash0}
git log --format=fuller
%patch -P 0 -p1 -b .bundle~
%patch -P 1 -p0 -b .shrlib~
%patch -P 2 -p0 -b .hdr~
%patch -P 3 -p0 -b .build~
# Patch4 (abc-format.patch) no longer applies to this snapshot and is disabled:
# patch -P 4 -p0 -b .name~
%patch -P 100 -p0 -b .gcc11~

# Do not use the bundled libraries
rm -fr lib src/misc/{bzlib,zlib}

# Set the version number in the man page
sed 's/@VERSION@/%{version} (%{scdate0})/' %{SOURCE1} > %{name}.1
touch -r %{SOURCE1} %{name}.1

%build
export CFLAGS="%{optflags} -DNDEBUG -Wno-unused-variable"
export CXXFLAGS="$CFLAGS"
# abc's CMakeLists defaults to static libraries (BUILD_SHARED_LIBS=OFF), but this
# package ships libabc as a shared library with a soname, so ask for it explicitly.
%cmake . \
      -DBUILD_SHARED_LIBS=ON \
      -DCMAKE_SKIP_RPATH=YES \
      -DCMAKE_SKIP_INSTALL_RPATH=YES \
      -DCMAKE_VERBOSE_MAKEFILE=OFF \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DABC_SKIP_TESTS=ON

# abc's CMakeLists declares libabc with EXCLUDE_FROM_ALL -- it used to come out
# anyway as a dependency of the abc binary, but with cmake 4 (fedora-44 and
# newer) it no longer does and %%install then found no libabc.so.0.0.0.  Ask for
# both targets explicitly so the shared library the package ships is always
# built, on every chroot and every cmake generation.  (%% is needed above: rpm
# expands macros inside comments and a bare %%install aborts the parse.)
make ABC_MAKE_VERBOSE=0 ABC_USE_STDINT_H=1 %{?_smp_mflags} abc libabc


%install
# Install the library
mkdir -p %{buildroot}%{_libdir}
install -p -m 0755 lib%{name}.so.0.0.0 %{buildroot}%{_libdir}
ln -s lib%{name}.so.0.0.0 %{buildroot}%{_libdir}/lib%{name}.so.0
ln -s lib%{name}.so.0 %{buildroot}%{_libdir}/lib%{name}.so

# Install the header files
pushd src
mkdir -p %{buildroot}%{_includedir}/%{name}
tar -cBf - $(find -O3 . -name \*.h) | \
  (cd %{buildroot}%{_includedir}/%{name}; tar -xBf -)
popd

# Install the binary
mkdir -p %{buildroot}%{_bindir}
install -p -m 0755 %{name} %{buildroot}%{_bindir}

# Install the man page
mkdir -p %{buildroot}%{_mandir}/man1
install -p -m 0644 %{name}.1 %{buildroot}%{_mandir}/man1


%files
%doc README.md readmeaig
%{_bindir}/%{name}
%{_mandir}/man1/%{name}*

%files libs
%license copyright.txt
%{_libdir}/lib%{name}.so.*

%files devel
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so


%changelog
* Tue Sep 22 2026 Cristian Balint <cristian.balint@gmail.com> - 1.02
- Update git pin to current master (24cec094)
- Rebase the Fedora patches onto the new snapshot and unbundle zlib in
  src/map/scl/sclLiberty.c (new since the previous pin)
- Build libabc as a shared library (upstream defaults to static now)

* Sun Jul 25 2021 Cristian Balint <cristian.balint@gmail.com>
- upstream git relases

* Fri Jan 31 2020 Gabriel Somlo <gsomlo@gmail.com> - 1.01-26.git20200127
- Update to latest git snapshot

