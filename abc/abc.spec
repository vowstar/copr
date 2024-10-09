%global pkgvers 0
%global scdate0 20241009
%global schash0 707442e0915dd7fdbfc5742b04ef16429373075a
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
%global _default_patch_fuzz 100

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
# % patch -P 4 -p0 -b .name~
%patch -P 100 -p0 -b .gcc11~

# Do not use the bundled libraries
rm -fr lib src/misc/{bzlib,zlib}

# Set the version number in the man page
sed 's/@VERSION@/%{version} (%{gitdate})/' %{SOURCE1} > %{name}.1
touch -r %{SOURCE1} %{name}.1

%build
export CFLAGS="%{optflags} -DNDEBUG -Wno-unused-variable"
export CXXFLAGS="$CFLAGS"
%cmake . \
      -DCMAKE_SKIP_RPATH=YES \
      -DCMAKE_SKIP_INSTALL_RPATH=YES \
      -DCMAKE_VERBOSE_MAKEFILE=OFF \
      -DCMAKE_BUILD_TYPE=RelWithDebInfo \
      -DABC_SKIP_TESTS=ON

make ABC_MAKE_VERBOSE=0 ABC_USE_STDINT_H=1 %{?_smp_mflags}


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
* Sun Jul 25 2021 Cristian Balint <cristian.balint@gmail.com>
- upstream git relases

* Fri Jan 31 2020 Gabriel Somlo <gsomlo@gmail.com> - 1.01-26.git20200127
- Update to latest git snapshot

