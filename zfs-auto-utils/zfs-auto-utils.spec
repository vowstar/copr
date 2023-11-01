%global debug_package %{nil}

Name:		zfs-auto-utils
Version:	1.0.0
Release:	1%{?dist}
Summary:	ZFS Automatic Scrub/Trim for Linux

Group:		Applications/System
License:	GPL2
URL:		https://github.com/vowstar/%{name}
Source0:	%{url}/archive/%{version}.tar.gz

BuildRequires:	make
# Requires:

%description
ZFS Automatic Scrub/Trim for Linux.
This package is ported from debian to facilitate use on other
distributions. This package renames some properties to make them more
consistent when used with zfs-auto-snapshot.
Auto TRIM is implemented using a custom per-pool property:
com.sun:auto-trim
By default, these TRIM jobs are scheduled on the first Sunday of every
month. The completion speed depends on the disks size, disk speed and
workload pattern. Cheap QLC disks could take considerable more time than
very expensive enterprise graded NVMe disks.
When com.sun:auto-trim is not present in pool, or the property is
present but value is empty/invalid, they are treated as auto.
Auto Scrub is implemented using a custom per-pool property:
com.sun:auto-scrub
By default this have a cron job entry to scrub all pools on the second
Sunday of every month at 24 minutes past midnight.
See /etc/cron.d/zfsutils-linux and /usr/libexec/zfs/scrub for details
It is possible to disable this by setting a zfs user defined property on
the root dataset for a pool.


%prep
%setup -q -n %{name}-%{version}
sed -i s@/usr/local@/usr@ Makefile


%build


%install
%make_install


%files
%{_sysconfdir}/cron.d/zfsutils-linux
%{_libexecdir}/zfs/scrub
%{_libexecdir}/zfs/trim


%changelog
