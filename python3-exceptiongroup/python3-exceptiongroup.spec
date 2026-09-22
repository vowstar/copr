# python3-exceptiongroup: the PEP 654 exception-group backport.
#
# Packaged because python3-cocotb 2.1.0 requires it on Python < 3.11 and no
# Enterprise Linux 9 repository ships it (dnf provides python3dist(exceptiongroup)
# finds nothing), which made the cocotb RPM impossible to install there.
#
# Upstream is a PEP 621 project built with flit_scm, and el9's setuptools (53)
# cannot build PEP 621 projects at all, so the wheel is built in an isolated
# environment and fetches its own backend (the COPR project has networking on).
# Same approach as python3-find-libpython.
#
# Version 1.2.2 rather than 1.3.1 on purpose: 1.3.1 requires
# "typing-extensions >= 4.6", and Enterprise Linux 9 has no typing-extensions
# package at all, so 1.3.1's RPM would not be installable.  cocotb only asks for
# "exceptiongroup" with no minimum, so 1.2.2 satisfies it and has no runtime
# dependencies of its own.
#
# COPR chroots: same set as python3-cocotb (el9 family + fedora-43/44), set via
#   copr-cli build-package -r epel-9-x86_64 -r rhel-9-x86_64 \
#     -r centos-stream-9-x86_64 -r centos-stream+epel-next-9-x86_64 \
#     -r fedora-43-x86_64 -r fedora-44-x86_64 \
#     --name python3-exceptiongroup vowstar/eda
# The el8 family is excluded: flit_scm is a PEP 517 backend needing python
# >= 3.8 and el8's platform python3 is 3.6, so %generate_buildrequires fails
# there.  This package exists to satisfy cocotb on el9, which is el9-only too.

Name:           python3-exceptiongroup
Version:        1.2.2
Release:        1%{?dist}
Summary:        Backport of PEP 654 (exception groups)

License:        MIT
URL:            https://github.com/agronholm/exceptiongroup
Source0:        https://files.pythonhosted.org/packages/09/35/2495c4ac46b980e4ca1f6ad6db102322ef3ad2410b79fdde159a4b0f3b92/exceptiongroup-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
BuildRequires:  python3-pip

%description
This is a backport of the BaseExceptionGroup and ExceptionGroup classes from
Python 3.11 to Python 3.7 and later, together with the catch() helper that
splits an exception group into the parts matched by given filters.

It is needed by cocotb 2.x, which reports test failures through exception groups
when it runs on Python older than 3.11.

%prep
%autosetup -n exceptiongroup-%{version}

%generate_buildrequires
%pyproject_buildrequires -N

%build
%{python3} -m pip wheel --no-deps --wheel-dir %{_pyproject_wheeldir} .

%install
%pyproject_install
%pyproject_save_files exceptiongroup

%files -f %{pyproject_files}
%license LICENSE
%doc README.rst

%changelog
* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 1.2.2-1
- Initial package: cocotb 2.1.0 requires exceptiongroup on Python < 3.11 and no
  EL9 repository provides it
