# help2man for CentOS 7.  Build dependency of verilator (its Makefile generates
# verilator_gantt.1 / verilator_profcfunc.1 with help2man) and of any other
# package that does the same.  CentOS 7 has no help2man package reachable from
# this cluster, hence building it from the GNU source.
#
# Build (as vowstar, from ~/rpmbuild):  rpmbuild -bb SPECS/help2man.spec
# Install (as root):                    rpm -Uvh RPMS/noarch/help2man-1.49.3-1.el7.noarch.rpm

Name:           help2man
Version:        1.49.3
Release:        1%{?dist}
Summary:        Create simple man pages from --help output
License:        GPL-3.0-or-later
URL:            https://www.gnu.org/software/help2man/
Source0:        https://ftp.gnu.org/gnu/help2man/help2man-%{version}.tar.xz
BuildArch:      noarch

# configure.ac has AC_PROG_CC and the build compiles bindtextdomain.c into
# bindtextdomain.so, so a C compiler is required even though the package is
# noarch (and even with --disable-nls).
BuildRequires:  gcc
BuildRequires:  perl
BuildRequires:  make
BuildRequires:  sed

%description
help2man is a tool for automatically generating simple manual pages from
program --help and --version output.

%prep
%setup -q

%build
%configure --disable-nls
%make_build

%install
%make_install

%files
%{_bindir}/help2man
%{_infodir}/help2man.info*
%{_mandir}/man1/help2man.1*

%changelog
* Wed Sep 16 2026 vowstar <vowstar@gmail.com> - 1.49.3-1
- Initial package, built to satisfy verilator's build requirement on el7
- BuildRequires gcc: verified on Rocky Linux 8, where a clean chroot otherwise
  fails with "configure: error: no acceptable C compiler found in $PATH"
