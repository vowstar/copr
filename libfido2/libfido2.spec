# libfido2, packaged here because the el8 chroots that have no EPEL carry no
# libfido2-devel, and openssh is built --with-security-key-builtin (FIDO/U2F
# security keys) which needs its header and library at build time and the shared
# library at run time.
#
# Version and soname (libfido2.so.1) match what EPEL 8 ships, so this package is
# interchangeable with EPEL's where both are available.  libcbor, the other
# dependency missing from a bare el8 buildroot, comes from this same repository;
# hidapi likewise (pkgconfig(hidapi-hidraw) is provided by the hidapi package
# built here, so no EPEL is required for this chain).
#
# Build (as vowstar, from ~/rpmbuild): rpmbuild -bb SPECS/libfido2.spec
# Install (as root):                    rpm -Uvh RPMS/x86_64/libfido2-1.11.0-1.el8.x86_64.rpm

Name:           libfido2
Version:        1.11.0
Release:        1%{?dist}
Summary:        FIDO2 library
License:        BSD-2-Clause
URL:            https://github.com/Yubico/libfido2
Source0:        https://developers.yubico.com/%{name}/Releases/%{name}-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  pkgconfig(hidapi-hidraw)
BuildRequires:  pkgconfig(libcbor)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(zlib)

%description
libfido2 is an open source library to support the FIDO2 protocol.  FIDO2 is an
open authentication standard that consists of the W3C Web Authentication
specification (WebAuthn API), and the Client to Authentication Protocol (CTAP).
CTAP is an application layer protocol used for communication between a client
(browser) or a platform (operating system) with an external authentication
device (for example the Yubico Security Key).

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
libfido2-devel contains the libraries and header files needed to develop
programs that use libfido2.

%package -n fido2-tools
Summary:        FIDO2 tools
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description -n fido2-tools
FIDO2 command line tools to access and configure a FIDO2 compliant
authentication device.

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
%license LICENSE
%doc NEWS README.adoc
%{_libdir}/libfido2.so.1*

%files devel
%{_includedir}/fido.h
%{_includedir}/fido/
%{_libdir}/libfido2.so
%{_libdir}/pkgconfig/libfido2.pc
%{_mandir}/man3/*

%files -n fido2-tools
%{_bindir}/fido2-*
%{_mandir}/man1/*

%changelog
* Mon Sep 22 2026 vowstar <vowstar@gmail.com> - 1.11.0-1
- Initial package: libfido2 1.11.0 for the el8 chroots without EPEL, needed by
  openssh's --with-security-key-builtin FIDO support
