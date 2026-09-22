%global pkgvers 0
%global scdate0 20260716
%global schash0 d5243a25c488dfe751ef218828f13516e04ea2ba
%global branch0 master
%global source0 https://github.com/msteveb/jimtcl.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           jimtcl
Version:        0.84
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        A small embeddable Tcl interpreter
License:        BSD

URL:            http://jim.tcl.tk

BuildRequires:  gcc gcc-c++ asciidoc make git tcl
BuildRequires:  pkgconfig(openssl) pkgconfig(zlib)
BuildRequires:  sqlite-devel readline-devel
%if !(0%{?rhel})
BuildRequires: hiredis-devel json-devel
%endif

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
* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 0.84-20260716.0.gitd5243a25
- Update to upstream 0.84 (git commit d5243a25)

* Tue Aug 17 2021 Cristian Balint <cristian.balint@gmail.com>
- github update releases
