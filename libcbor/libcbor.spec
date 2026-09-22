# libcbor, packaged here because the el8 chroots that have no EPEL carry no
# libcbor, and libfido2 -- which openssh links for FIDO/U2F security key support
# (--with-security-key-builtin) -- cannot be built without it.
#
# Version and soname (libcbor.so.0) match what EPEL 8 ships, so this package is
# interchangeable with EPEL's where both are available.
#
# Build (as vowstar, from ~/rpmbuild): rpmbuild -bb SPECS/libcbor.spec
# Install (as root):                    rpm -Uvh RPMS/x86_64/libcbor-0.7.0-1.el8.x86_64.rpm

Name:           libcbor
Version:        0.7.0
Release:        1%{?dist}
Summary:        A CBOR parsing library
License:        MIT
URL:            https://libcbor.org/
Source0:        https://github.com/PJK/libcbor/archive/v%{version}/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  make

%description
libcbor is a C library for parsing and generating CBOR, the general-purpose
schema-less binary data format described in RFC 7049.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
libcbor-devel contains the libraries and header files needed to develop
programs that use libcbor.

%prep
%setup -q

%build
%cmake -DCMAKE_BUILD_TYPE=Release
%cmake_build

%install
%cmake_install
# Only the shared library is packaged; the packaging guidelines here do not want
# a static archive in the -devel subpackage.
find %{buildroot} -type f -name "*.a" -delete -print

%ldconfig_scriptlets

%files
%license LICENSE.md
%doc README.md
%{_libdir}/libcbor.so.0*

%files devel
%{_includedir}/cbor.h
%{_includedir}/cbor/
%{_libdir}/libcbor.so
%{_libdir}/pkgconfig/libcbor.pc

%changelog
* Mon Sep 22 2026 vowstar <vowstar@gmail.com> - 0.7.0-1
- Initial package: libcbor 0.7.0 for the el8 chroots without EPEL, needed by
  libfido2, which openssh links for FIDO security key support
