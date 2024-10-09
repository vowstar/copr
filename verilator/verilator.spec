%global pkgvers 0
%global scdate0 20241009
%global schash0 041f6603c3cb2c71d42fa3629dcff0eac118b993
%global branch0 master
%global source0 https://github.com/verilator/verilator.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

%define with_docs 0

Name:           verilator
Version:        %(curl -s https://raw.githubusercontent.com/verilator/verilator/%{schash0}/CMakeLists.txt | sed -n '/project/,/LANG/p' | grep VERSION | awk '{print $2}')
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        A fast simulator for synthesizable Verilog
License:        LGPLv3 or Artistic 2.0

URL:            http://www.veripool.com/%{name}.html

BuildRequires:  git sed automake python3 help2man
BuildRequires:  bison coreutils findutils flex gcc-c++
BuildRequires:  perl-generators perl-interpreter perl-version
BuildRequires:  perl(Getopt::Long) perl(IO::File) perl(Pod::Usage)
BuildRequires:  perl(strict) perl(vars) perl(Data::Dumper) perl(Time::HiRes)
BuildRequires:  perl(Digest::MD5) perl(FindBin) perl-Pod-Html
%if %{with_docs}
BuildRequires:  perl-Pod-LaTeX
BuildRequires:  python3-sphinx python3-sphinx_rtd_theme config(latexmk)
BuildRequires:  tex(tex) tex(latex) tex(fncychap.sty) tex(wrapfig.sty)
BuildRequires:  tex(capt-of.sty) tex(framed.sty) tex(upquote.sty)
BuildRequires:  tex(needspace.sty) tex(tabulary.sty) tex(tgtermes.sty)
BuildRequires:  tex(pgfpict2e.sty)
%endif

%description
Verilator is the fastest free Verilog HDL simulator. It compiles
synthesizable Verilog, plus some PSL, SystemVerilog and Synthesis
assertions into C++ or SystemC code. It is designed for large projects
where fast simulation performance is of primary concern, and is
especially well suited to create executable models of CPUs for
embedded software design teams.


%prep
%setup -T -c -n %{name}
git clone --depth 1 -n -b %{branch0} %{source0} .
git fetch --depth 1 origin %{schash0}
git reset --hard %{schash0}
git log --format=fuller


%build
sed -i '1 i #include <memory>' src/V3File.h
find . -name .gitignore -delete
export VERILATOR_ROOT=%{_datadir}/%{name}
aclocal
autoconf
%configure \
    --disable-ccwarn \
    --enable-defenv \
    --disable-longtests

find -name Makefile_obj -exec sed -i \
    -e 's|^\(COPT = .*\)|\1 %{optflags}|' \
    -e 's|^#LDFLAGS += .*|LDFLAGS += %{__global_ldflags}|' \
    {} \;
%if %{with_docs}
make docs
%endif
%make_build


%check
make test


%install
%make_install
mkdir -p %{buildroot}%{_libdir}/pkgconfig
mv %{buildroot}%{_datadir}/pkgconfig/verilator.pc %{buildroot}%{_libdir}/pkgconfig


%files
%license Artistic LICENSE
%doc Changes README*
%if %{with_docs}
%doc verilator.pdf
%endif
%doc examples/
%{_datadir}/verilator
%{_bindir}/verilator
%{_bindir}/verilator_bin
%{_bindir}/verilator_bin_dbg
%{_bindir}/verilator_coverage
%{_bindir}/verilator_coverage_bin_dbg
%{_bindir}/verilator_gantt
%{_bindir}/verilator_profcfunc
%{_libdir}/pkgconfig/verilator.pc
%{_mandir}/man1/verilator.1.gz
%{_mandir}/man1/verilator_gantt.1.gz
%{_mandir}/man1/verilator_profcfunc.1.gz
%{_mandir}/man1/verilator_coverage.1.gz


%changelog
* Wed Mar 27 2019 Balint Cristian <cristian.balint@gmail.com>
- github update releases
