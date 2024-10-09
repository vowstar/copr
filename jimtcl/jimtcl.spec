%global pkgvers 0
%global scdate0 20240920
%global schash0 1273201def190161c3e39fbe42bbfea4d642d8a3
%global branch0 master
%global source0 https://github.com/msteveb/jimtcl.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           jimtcl
Version:        0.83
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        A small embeddable Tcl interpreter
License:        BSD

URL:            http://jim.tcl.tk

BuildRequires:  gcc gcc-c++ asciidoc make git tcl
BuildRequires:  pkgconfig(openssl) pkgconfig(zlib)
BuildRequires:  sqlite-devel hiredis-devel json-devel readline-devel

%description
Jim is an opensource small-footprint implementation of the Tcl programming
language. It implements a large subset of Tcl and adds new features like 
references with garbage collection, closures, built-in Object Oriented 
Programming system, Functional Programming commands, first-class arrays and 
UTF-8 support.

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
rm -rf sqlite3
# gcc13
sed -i '1i #include <stdio.h>' ./jim-readline.c

%build
export CC=gcc
export LD=ld
export AR=ar
export RANLIB=ranlib
export STRIP=strip
%configure \
  --shared \
  --disable-option-checking \
  --allextmod \
  --docdir=%{_datadir}/doc/%{name}
%make_build


%install
%make_install INSTALL_DOCS=nodocs
rm %{buildroot}/%{_libdir}/jim/README.extensions


%files
%license LICENSE
%doc AUTHORS README
%doc %{_datadir}/doc/%{name}/Tcl.html
%{_bindir}/jimdb
%{_bindir}/jimsh
%dir %{_libdir}/jim
%{_libdir}/jim/*.tcl
%{_libdir}/jim/*.so
%{_libdir}/libjim.so.*


%files devel
%doc README.* STYLE
%{_includedir}/*
%{_bindir}/build-jim-ext
%{_libdir}/libjim.so
%{_libdir}/pkgconfig/jimtcl.pc

%changelog
* Tue Aug 17 2021 Cristian Balint <cristian.balint@gmail.com>
- github update releases
