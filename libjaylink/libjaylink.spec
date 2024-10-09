%global pkgvers 0
%global scdate0 20240704
%global schash0 fed1ad39316ad63db084c3d751aabe39643e4220
%global branch0 master
%global source0 https://gitlab.zapb.de/libjaylink/libjaylink.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           libjaylink
Version:        0.3.1
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
%__sed -e 's/MODE="664", GROUP="plugdev"/TAG+="uaccess"/g' contrib/60-libjaylink.rules > %{buildroot}/usr/lib/udev/rules.d/60-libjaylink.rules

%ldconfig_scriptlets

%files
%license COPYING
%doc README.md NEWS
%{_libdir}/*.so.*
%{_prefix}/lib/udev/rules.d/*

%files devel
%doc HACKING
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%changelog
* Tue Aug 17 2021 Cristian Balint <cristian.balint@gmail.com>
- github update releases
