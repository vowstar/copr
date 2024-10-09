%global pkgvers 0
%global scdate0 20241009
%global schash0 a5968e404756487c67863907b02d5a182a6007be
%global branch0 main
%global source0 https://github.com/YosysHQ/yosys.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

%define with_doc 0

Name:           yosys
Version:        0.46
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        Yosys Open SYnthesis Suite, including Verilog synthesizer
License:        ISC and MIT

URL:            http://bygone.clairexen.net/yosys

Patch1:         yosys-cfginc.patch
Patch2:         yosys-mancfginc.patch
Patch3:         %{name}-gcc11.patch

BuildRequires:  git gcc-c++ bison flex pkgconfig txt2man
BuildRequires:  python3 tcl-devel libffi-devel readline-devel
BuildRequires:  abc iverilog graphviz

%define manual %{nil}

%if %{with_doc} && 0%{?fedora}
%define manual "manual"
BuildRequires:  config(lyx-common)
BuildRequires:  tex(tex) tex(latex) tex(IEEEtran.cls) tex(libertine.sty)
BuildRequires:  tex(units.sty) tex(algpseudocode.sty) tex(multirow.sty)
BuildRequires:  tex(skull.sty) tex(subfigure.sty) tex(moreverb.sty) tex(epsf.sty)
BuildRequires:  tex(dsfont.sty) tex(algorithm2e.sty) tex(multibib.sty)
%endif

Requires:       abc graphviz python-xdot
Requires:       %{name}-share = %{version}-%{release}

%global _lto_cflags %{nil}
%global _default_patch_fuzz 100

%description
Yosys is a framework for Verilog RTL synthesis. It currently has
extensive Verilog-2005 support and provides a basic set of synthesis
algorithms for various application domains.


%package        doc
Summary:        Documentation for Yosys synthesizer

%description    doc
Documentation for Yosys synthesizer.


%package        share
Summary:        Architecture-independent Yosys files
BuildArch:      noarch

%description    share
Architecture-independent Yosys files.


%package        devel
Summary:        Development files to build Yosys synthesizer plugins
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       tcl-devel

%description    devel
Development files to build Yosys synthesizer plugins.


%prep
%setup -T -c -n %{name}
git clone --depth 1 -n -b %{branch0} %{source0} .
git fetch --depth 1 origin %{schash0}
git reset --hard %{schash0}
git log --format=fuller

%patch -P 1 -p1 -b .cfginc
#patch -P 2 -p1 -b .mancfginc

# swap libertine (or helvet)
#find manual -name '*.tex' -exec sed -i 's|{luximono}|{libertine}|g' {} +
# fix shebangs
find . -name '*.py' -exec sed -i 's|/usr/bin/env python3|/usr/bin/python3|' {} +


%build
make config-gcc
%set_build_flags
make %{?_smp_mflags} PREFIX="%{_prefix}" ABCEXTERNAL=%{_bindir}/abc PRETTY=0 all %{manual}


%install
%make_install PREFIX="%{_prefix}" ABCEXTERNAL=%{_bindir}/abc STRIP=/bin/true

# move include files to includedir
install -d -m0755 %{buildroot}%{_includedir}
mv %{buildroot}%{_datarootdir}/%{name}/include %{buildroot}%{_includedir}/%{name}

%if %{with_doc} && 0%{?fedora}
# install documentation
install -d -m0755 %{buildroot}%{_docdir}/%{name}
install -m 0644 manual/*.pdf %{buildroot}%{_docdir}/%{name}
%endif

%files
%doc README.md
%license COPYING
%{_bindir}/%{name}
%{_bindir}/%{name}-*

%files share
%{_datarootdir}/%{name}

%files doc
%{_docdir}/%{name}

%files devel
%{_bindir}/%{name}-config
%{_includedir}/%{name}


%changelog
* Sat Feb 06 2021 Cristian Balint <cristian.balint@gmail.com>
- github upstream releases

* Sat Oct 17 2020 Jeff Law <law@redhat.com> - 0.9-8
- Fix missing #include for gcc-11
