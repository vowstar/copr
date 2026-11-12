%global debug_package %{nil}

Name:		zfs-auto-snapshot
Version:	1.2.4
Release:	2%{?dist}
Summary:	ZFS Automatic Snapshot Service for Linux

Group:		Applications/System
License:	GPL2
URL:		https://github.com/zfsonlinux/%{name}
Source0:	%{url}/archive/upstream/%{version}/%{name}-upstream-%{version}.tar.gz
Patch0:     0001-Fix-broken-cron-scripts.patch
Patch1:     0002-Found-a-way-to-exec-the-process-and-yet-have-it-work.patch

BuildRequires:	gcc, gcc-c++, glibc-devel, make
Requires: glibc

%description
An alternative implementation of the zfs-auto-snapshot service for Linux
that is compatible with zfs-linux and zfs-fuse.

Automatically create, rotazte, and destroy periodic ZFS snapshots. This is
the utility that creates the @zfs-auto-snap_frequent, @zfs-auto-snap_hourly,
@zfs-auto-snap_daily, @zfs-auto-snap_weekly, and @zfs-auto-snap_monthly
snapshots if it is installed.

This program is a posixly correct bourne shell script.  It depends only on
the zfs utilities and cron, and can run in the dash shell.


%prep
%setup -q -n %{name}-upstream-%{version}
#%%patch -P 0 -p1
#%%patch -P 1 -p1
sed -i s@/usr/local@/usr@ Makefile


%build


%install
%make_install


%files
%config(noreplace) %{_sysconfdir}/cron.d/zfs-auto-snapshot
%config(noreplace) %{_sysconfdir}/cron.hourly/zfs-auto-snapshot
%config(noreplace) %{_sysconfdir}/cron.daily/zfs-auto-snapshot
%config(noreplace) %{_sysconfdir}/cron.weekly/zfs-auto-snapshot
%config(noreplace) %{_sysconfdir}/cron.monthly/zfs-auto-snapshot
%{_mandir}/man8/zfs-auto-snapshot.8.gz
%{_sbindir}/zfs-auto-snapshot


%changelog
* Thu Nov 12 2026 Huang Rui <vowstar@gmail.com> - 1.2.4-2
- Mark cron files as %config(noreplace) so local snapshot-retention edits
  survive package upgrades.
