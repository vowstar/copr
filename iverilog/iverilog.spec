%global pkgvers 0
%global scdate0 20241009
%global schash0 25a84d5cfcecf67bfb7734929a1df98c4b137ce6
%global branch0 master
%global source0 https://github.com/steveicarus/iverilog.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           iverilog
Version:        %(curl -s https://raw.githubusercontent.com/steveicarus/iverilog/%{schash0}/version_base.h | grep "define VERSION_M" | grep -o '[^ ]*$' | sed ':a;N;$!ba;s/\n/./g')
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        Icarus Verilog is a verilog compiler and simulator
License:        GPLv2

URL:            http://iverilog.icarus.com

BuildRequires:  git gcc-c++ autoconf bison flex gperf
BuildRequires:  bzip2-devel readline-devel zlib-devel

%description
Icarus Verilog is a Verilog compiler that generates a variety of
engineering formats, including simulation. It strives to be true
to the IEEE-1364 standard.


%prep
%setup -T -c -n %{name}
git clone --depth 1 -n -b %{branch0} %{source0} .
git fetch --depth 1 origin %{schash0}
git reset --hard %{schash0}
git log --format=fuller


%build
%global optflags %(echo "%{optflags}" | sed 's|-Werror=format-security||')
chmod +x autoconf.sh
sh autoconf.sh
%configure
make %{?_smp_mflags}


%install
make    prefix=%{buildroot}%{_prefix} \
        bindir=%{buildroot}%{_bindir} \
        libdir=%{buildroot}%{_libdir} \
        libdir64=%{buildroot}%{_libdir} \
        includedir=%{buildroot}%{_includedir} \
        mandir=%{buildroot}%{_mandir}  \
        vpidir=%{buildroot}%{_libdir}/ivl/ \
        INSTALL="install -p" \
install


%files
%doc README.md
%doc examples/
%license COPYING
%{_bindir}/*
%{_libdir}/ivl
%{_mandir}/man1/*
# headers for PLI: This is intended to be used by the user.
%{_includedir}/*.h
# RHBZ 480531
%{_libdir}/*.a


%changelog
* Sat Feb 06 2021 Cristian Balint <cristian.balint@gmail.com>
- upstream git builds

* Sun Feb 17 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 10_2-5
- Rebuild for readline 8.0
