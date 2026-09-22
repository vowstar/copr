%global pkgvers 0
%global scdate0 20260828
%global schash0 5b9ab7b06249af69d349c3ce8b29e8769845071e
%global branch0 master
%global source0 https://gitlab.zapb.de/libjaylink/libjaylink.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           libjaylink
Version:        0.5.0
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        Library for SEGGER J-Link and compatible devices
License:        GPLv2+

URL:            https://gitlab.zapb.de/libjaylink/libjaylink

BuildRequires:  gcc make git libtool autoconf automake
BuildRequires:  pkgconfig(libusb-1.0)

%description
libjaylink is a shared library written in C to access SEGGER J-Link
and compatible devices.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%prep
%setup -T -c -n %{name}
git clone --depth 1 -n -b %{branch0} %{source0} .
git fetch --depth 1 origin %{schash0}
git reset --hard %{schash0}
git log --format=fuller


%build
sed -i '/AC_PROG_CC_C99/d' configure.ac
./autogen.sh
%configure --disable-static
%make_build


%install
%make_install
find %{buildroot} -name '*.la' -exec rm -f {} ';'
%__mkdir -p %{buildroot}/usr/lib/udev/rules.d/
%__sed -e 's/MODE="660", GROUP="plugdev", //g' contrib/60-libjaylink.rules > %{buildroot}/usr/lib/udev/rules.d/60-libjaylink.rules

%ldconfig_scriptlets

%files
%license COPYING
%doc README.md NEWS
%{_libdir}/*.so.*
%{_prefix}/lib/udev/rules.d/*

%files devel
%doc HACKING.md
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%changelog
* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 0.5.0-20260828.0.git5b9ab7b0
- Update to upstream 0.5.0 (git commit 5b9ab7b0)
- HACKING was renamed to HACKING.md upstream
- Refresh the udev rule mangling for the upstream MODE="660" rules file

* Tue Aug 17 2021 Cristian Balint <cristian.balint@gmail.com>
- github update releases
