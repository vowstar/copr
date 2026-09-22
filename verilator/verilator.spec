# Verilator, built from the upstream GitHub tag tarball.
#
# Builds on both RHEL/CentOS 8 (ice2) and CentOS 7 (ucun1/ucun2):
#
#   el8: system gcc-c++ 8.5, which is C++17 capable, links system libstdc++.
#   el7: system gcc 4.8 is NOT C++17 capable, so the build uses devtoolset-11.
#        That toolset has no runtime libstdc++ of its own (its libstdc++.so
#        linker script points at /usr/lib64/libstdc++.so.6 = GCC 4.8), so the
#        el7 binary is additionally linked with -static-libstdc++ -static-libgcc.
#        Without that the binary needs GLIBCXX_3.4.2x symbols that the el7
#        userland does not have.
#
# Build (as the unprivileged user, from ~/rpmbuild):
#   rpmbuild -bb SPECS/verilator.spec
# Install (as root):
#   rpm -Uvh RPMS/x86_64/verilator-5.052-1.elN.x86_64.rpm
#
# Build-time Python: verilator's astgen uses the walrus operator, so the build
# needs python3 >= 3.8, and its test driver (test_regress/driver.py) uses
# structural pattern matching, so %check needs python3 >= 3.10.  ice2 has
# /usr/bin/python3.12; ucun1 has only 3.6 and no network, so it uses the private
# interpreter in ~/opt/python3.11 -- put it on PATH when invoking rpmbuild there:
#   PATH=$HOME/opt/python3.11/bin:$PATH rpmbuild -bb SPECS/verilator.spec
# The *installed* package is unaffected: verilator_gantt / verilator_profcfunc
# run fine on the el7 system python3.6 (only the build-time scripts need 3.8),
# and include/verilated.mk refers to plain "python3" -- never to the build-time
# interpreter -- so the package only Requires: python3.
#
# Runtime C++ compiler (what compiles the models verilator emits):
#   include/verilated.mk sets CFG_CXXFLAGS_STD_NEWEST = -std=gnu++17, so a plain
#   design needs a C++17 compiler (el8 gcc 8.5 and el7 devtoolset-11 are fine).
#   A design using timing (--timing, e.g. "always #5 clk = ~clk") additionally
#   includes include/verilated_timing.h, which needs a compiler with coroutines
#   (gcc >= 10): on el8 the system gcc 8.5 fails with
#     verilated_timing.h:53:11: fatal error: coroutine: No such file or directory
#   That is an upstream requirement, not a packaging bug (Fedora's verilator has
#   no compiler Requires either); el8 users need gcc-toolset-N (10+) plus
#   -std=c++20 for the model, which the appstream repo provides:
#     . /opt/rh/gcc-toolset-13/enable
#     verilator --binary ... -CFLAGS "-std=c++20"
#   (verified: with gcc-toolset-13 alone the model fails with
#    "the <coroutine> header requires -fcoroutines"; adding -std=c++20 builds
#    and the simulation passes)

%global buildjobs 24
%global with_docs 0

# Verilator's build scripts (astgen) need Python >= 3.8; the distro python3 is
# 3.6 on both el7 and el8.  Pick the newest python3.x in %{_bindir}; the default
# is plain python3 (correct on COPR/Fedora, and on ucun1 via the private
# /home/vowstar/opt/python3.11 -- override the macro explicitly when building
# there:  rpmbuild -bb --define 'buildpy /home/vowstar/opt/python3.11/bin/python3' SPECS/verilator.spec
# No nested command substitution here on purpose: COPR builds SRPMs with rpkg,
# whose spec parser trips over $( ) nested inside %( ).
%global buildpy %(p=%{_bindir}/python3; for v in 3.13 3.12 3.11 3.10 3.9 3.8; do if [ -x %{_bindir}/python$v ]; then p=%{_bindir}/python$v; break; fi; done; echo $p)

Name:           verilator
Version:        5.052
Release:        1%{?dist}
Summary:        A fast simulator for synthesizable Verilog
License:        LGPL-3.0-only OR Artistic-2.0
URL:            https://verilator.org
Source0:        https://github.com/verilator/verilator/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Build-time only: verilator's test driver (test_regress/driver.py) imports
# `distro`, which is packaged for py3.6 only on el7/el8 -- not for the newer
# python3.x the test suite itself needs.  Vendored for %check.
Source1:        https://files.pythonhosted.org/packages/fc/f8/98eea607f65de6527f8a2e8885fc8015d3e6f5775df186e443e0964a11c3/distro-1.9.0.tar.gz
BuildArch:      x86_64

%if 0%{?rhel} == 7
BuildRequires:  devtoolset-11-gcc-c++
%else
BuildRequires:  gcc-c++
%endif
BuildRequires:  binutils
BuildRequires:  make
BuildRequires:  sed
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  flex
BuildRequires:  bison
BuildRequires:  help2man
%if 0%{?rhel} == 8 || 0%{?rhel} == 9
# The platform python3 is 3.6 on el8 and 3.9 on el9, while src/astgen needs
# >= 3.8 (walrus operator) and %check's test_regress/driver.py needs >= 3.10
# (structural pattern matching at driver.py:2626).  python3.11 is a plain
# (non-modular) AppStream package on both el8 and el9, so this resolves in a
# clean chroot; it is also what the macro above picks as %{buildpy}.  Without it
# the el9/centos-stream-9 builds die in %check with "verilator's test driver
# needs python3 >= 3.10" (the 5.027 spec COPR built before did not hit this:
# that driver.py had no match statement yet).
BuildRequires:  python3.11
%endif
BuildRequires:  python3
BuildRequires:  perl
BuildRequires:  zlib-devel

Requires:       perl
Requires:       python3

%description
Verilator is the fastest free Verilog HDL simulator. It compiles
synthesizable Verilog, plus some PSL, SystemVerilog and Synthesis
assertions into C++ or SystemC code. It is designed for large projects
where fast simulation performance is of primary concern, and is
especially well suited to create executable models of CPUs for
embedded software design teams.


%prep
%setup -q


%build
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-11/enable
export LDFLAGS="%{?__global_ldflags} -static-libstdc++ -static-libgcc"
%endif
export PATH=%{_bindir}:$PATH
if ! %{buildpy} -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "ERROR: verilator's build scripts need python3 >= 3.8, found %{buildpy}"
    exit 1
fi
# PYTHON3 must not be in the environment when ./configure runs: configure.ac
# does AC_CHECK_PROG(PYTHON3,python3,python3), which keeps an inherited value,
# and @PYTHON3@ is substituted into include/verilated.mk, which the *installed*
# package uses at run time (VERILATOR_INCLUDER = $(PYTHON3) .../verilator_includer).
# Exporting the build-time interpreter therefore bakes its absolute path into the
# RPM and every model build on a machine without that exact path fails with
#   /bin/sh: /usr/bin/python3.11: No such file or directory
# (verified on Rocky 8).  Unset it for configure -- so the installed default is
# the plain "python3", which the runtime Requires: below provides -- and pass it
# on the make command line, where it overrides the makefile value for the build.
unset PYTHON3
# verilator bakes its default runtime location in at configure time
export VERILATOR_ROOT=%{_datadir}/%{name}
aclocal
autoconf
%configure \
    --disable-ccwarn \
    --disable-longtests

MAKEFLAGS=
%{__make} -j%{buildjobs} PYTHON3=%{buildpy} OBJCACHE_JOBS=-j%{buildjobs}


%check
%if 0%{?rhel} == 7
. /opt/rh/devtoolset-11/enable
%endif
# verilator's smoke tests are run through their own shebang
# (#!/usr/bin/env python3), so python3 on PATH must be good enough too, not just
# %{buildpy} (el8's /usr/bin/python3 is the 3.6 platform python).  PYTHON3 itself
# goes on the make command line for the same reason as in %build.
mkdir -p %{_builddir}/pypath
ln -sf %{buildpy} %{_builddir}/pypath/python3
%{__tar} xf %{SOURCE1} -C %{_builddir}
export PYTHONPATH=%{_builddir}/distro-1.9.0/src${PYTHONPATH:+:$PYTHONPATH}
export PATH=%{_builddir}/pypath:%{_bindir}:$PATH
if ! %{buildpy} -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
    echo "ERROR: verilator's test driver needs python3 >= 3.10 (it uses structural"
    echo "pattern matching), found %{buildpy}"
    exit 1
fi
MAKEFLAGS=
%{__make} -j%{buildjobs} PYTHON3=%{buildpy} test


%install
%make_install
mkdir -p %{buildroot}%{_libdir}/pkgconfig
mv %{buildroot}%{_datadir}/pkgconfig/verilator.pc %{buildroot}%{_libdir}/pkgconfig


%files
%license LICENSE
%doc Changes README.rst
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
* Wed Sep 16 2026 vowstar <vowstar@gmail.com> - 5.052-1
- Update to 5.052, vendor the release tarball instead of cloning at build time
- Build the el7 package with devtoolset-11 and a statically linked libstdc++
- Verified on Rocky Linux 8 and 9: add BuildRequires python3.11 (the platform
  python3 there is 3.6 and 3.9; src/astgen needs >= 3.8 and
  test_regress/driver.py needs >= 3.10) and BuildRequires help2man is satisfied
  on el8 from the powertools repo
- Do not export PYTHON3 into ./configure: AC_CHECK_PROG kept the build-time
  absolute path and baked it into include/verilated.mk, so model builds failed
  on machines without that interpreter.  PYTHON3 now goes on the make command
  line instead, and the installed default stays plain "python3"
* Wed Mar 27 2019 Balint Cristian <cristian.balint@gmail.com>
- github update releases
