# OpenSSH, the latest upstream portable release, packaged for RHEL/CentOS 8
# because the distribution's 8.0p1 is far behind.
#
# Upstream 10.5p1 requires OpenSSL 1.1.1 or newer (INSTALL in the tarball), which
# el8's openssl-1.1.1k satisfies, so no newer OpenSSL is needed.  Fedora's spec
# cannot be copied wholesale for exactly that reason: it pins
# "openssl-libs >= 1:3.5.0" and carries a patch stack that uses OpenSSL 3.5
# features, so this spec is built from the upstream tarball without patches.
#
# The packaging skeleton IS copied from Red Hat's 8.0p1 package (the el8 src.rpm
# and the c8s branch of centos-stream/rpms/openssh): the same three way split
# (openssh / openssh-clients / openssh-server), the same systemd units, the same
# sshd-keygen helper and the same /etc files, so installing this on el8 replaces
# the stock packages cleanly.  Those files are shipped as Sources below and are
# unmodified except where noted.
#
# Built without --with-security-key-builtin: that needs libfido2-devel, which
# el8 only has in EPEL, and the rhel-8/centos-stream-8 chroots would then fail to
# resolve build dependencies.  Add "BuildRequires: libfido2-devel" back together
# with the flag if you build on a host that has EPEL and want sk-* security keys.
#
# Build (as vowstar, from ~/rpmbuild):  rpmbuild -bb SPECS/openssh.spec
# Install (as root):                    dnf upgrade RPMS/x86_64/openssh-*.rpm

%global openssh_ver 10.5p1

Name:           openssh
Version:        %{openssh_ver}
Release:        1%{?dist}
Summary:        An open source implementation of SSH protocol version 2

License:        BSD-3-Clause AND BSD-2-Clause AND ISC AND SSH-OpenSSH AND ssh-keyscan AND snprintf
URL:            https://www.openssh.com/portable.html
Source0:        https://cdn.openbsd.org/pub/OpenBSD/OpenSSH/portable/openssh-%{version}.tar.gz
# Packaging files reused from Red Hat's el8 package, so that this package drops
# into an el8 system in the same shape as the distribution's openssh-server.
Source1:        sshd.pam
Source2:        sshd.sysconfig
Source3:        sshd.service
Source4:        sshd@.service
Source5:        sshd.socket
Source6:        sshd-keygen@.service
Source7:        sshd-keygen.target
Source8:        sshd-keygen
Source9:        sshd.tmpfiles

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  groff
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel
BuildRequires:  pam-devel
BuildRequires:  libselinux-devel
BuildRequires:  audit-libs-devel
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  libseccomp-devel
BuildRequires:  util-linux

Requires:       openssl-libs >= 1.1.1
Requires:       crypto-policies

%description
SSH (Secure SHell) is a program for logging into a remote machine and for
executing commands on a remote machine.  It is intended to replace rlogin and
rsh, and provide secure encrypted communications between two untrusted hosts
over an insecure network.

%package clients
Summary:        An open source SSH client applications
Requires:       %{name} = %{version}-%{release}

%description clients
OpenSSH is a free version of SSH (Secure SHell), a program for logging into a
remote machine and for executing commands on a remote machine.  This package
contains the ssh, scp, sftp, ssh-agent, ssh-add, ssh-copy-id, ssh-keyscan
clients and their manual pages.

%package server
Summary:        An open source SSH server daemon
Requires:       %{name} = %{version}-%{release}
Requires(pre):  /usr/sbin/useradd
Requires(pre):  /usr/sbin/groupadd
Requires:       pam

%description server
OpenSSH is a free version of SSH (Secure SHell), a program for logging into a
remote machine and for executing commands on a remote machine.  This package
contains the secure shell daemon (sshd), the systemd units that run it, its
default configuration and the helper that generates the host keys.

%prep
%autosetup -n openssh-%{version}

%build
%configure \
    --sysconfdir=%{_sysconfdir}/ssh \
    --libexecdir=%{_libexecdir}/openssh \
    --datadir=%{_datadir}/openssh \
    --with-default-path=/usr/local/bin:/usr/bin \
    --with-superuser-path=/usr/local/bin:/usr/bin \
    --with-privsep-path=%{_localstatedir}/empty/sshd \
    --disable-strip \
    --without-zlib-version-check \
    --with-ipaddr-display \
    --with-systemd \
    --with-mantype=man \
    --with-sandbox=seccomp_filter \
    --with-pam \
    --with-selinux \
    --with-audit=linux \
    --with-pie=no \
    --without-hardening

%{__make} %{?_smp_mflags}

%install
%{__make} install DESTDIR=%{buildroot}

# the privilege separation directory sshd chroots into
install -d -m 0711 %{buildroot}%{_localstatedir}/empty/sshd

# server side packaging files, taken from Red Hat's el8 openssh-server
install -d -m 0755 %{buildroot}%{_sysconfdir}/pam.d
install -p -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/sshd
install -d -m 0755 %{buildroot}%{_sysconfdir}/sysconfig
install -p -m 0640 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/sshd
install -d -m 0755 %{buildroot}%{_unitdir}
install -p -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/sshd.service
install -p -m 0644 %{SOURCE4} %{buildroot}%{_unitdir}/sshd@.service
install -p -m 0644 %{SOURCE5} %{buildroot}%{_unitdir}/sshd.socket
install -p -m 0644 %{SOURCE6} %{buildroot}%{_unitdir}/sshd-keygen@.service
install -p -m 0644 %{SOURCE7} %{buildroot}%{_unitdir}/sshd-keygen.target
install -d -m 0755 %{buildroot}%{_libexecdir}/openssh
install -p -m 0744 %{SOURCE8} %{buildroot}%{_libexecdir}/openssh/sshd-keygen
install -d -m 0755 %{buildroot}%{_tmpfilesdir}
install -p -m 0644 %{SOURCE9} %{buildroot}%{_tmpfilesdir}/openssh.conf

# upstream has no install rule for these two contrib files, but the
# distribution ships ssh-copy-id in openssh-clients
install -p -m 0755 contrib/ssh-copy-id %{buildroot}%{_bindir}/ssh-copy-id
install -d -m 0755 %{buildroot}%{_mandir}/man1
install -p -m 0644 contrib/ssh-copy-id.1 %{buildroot}%{_mandir}/man1/ssh-copy-id.1

# upstream installs sshd_config and ssh_config into %{_sysconfdir}/ssh; keep the
# distribution's permissions and make sure the drop-in include directories the
# units and RHEL conventions expect exist
install -d -m 0755 %{buildroot}%{_sysconfdir}/ssh/sshd_config.d
install -d -m 0755 %{buildroot}%{_sysconfdir}/ssh/ssh_config.d
chmod 0600 %{buildroot}%{_sysconfdir}/ssh/sshd_config

# the host keys are generated by sshd-keygen@.service (wanted by
# sshd-keygen.target, which sshd.service pulls in) and stay root owned at mode
# 0600: this build does not carry Red Hat's keyperm patch, so upstream's host key
# check rejects the 0640 root:ssh_keys scheme Red Hat uses
%pre server
getent group sshd >/dev/null || groupadd -r sshd
getent passwd sshd >/dev/null || \
    useradd -r -g sshd -d %{_localstatedir}/empty/sshd -s /sbin/nologin \
            -c "Privilege-separated SSH" sshd
exit 0

%post server
%systemd_post sshd.service sshd.socket

%preun server
%systemd_preun sshd.service sshd.socket

%postun server
%systemd_postun_with_restart sshd.service

%files
%license LICENCE
%doc CREDITS ChangeLog INSTALL OVERVIEW PROTOCOL* README*
%dir %{_sysconfdir}/ssh
%{_sysconfdir}/ssh/moduli
%{_bindir}/ssh-keygen
%{_libexecdir}/openssh/ssh-keysign
%{_mandir}/man1/ssh-keygen.1*
%{_mandir}/man5/moduli.5*
%{_mandir}/man8/ssh-keysign.8*

%files clients
%config(noreplace) %{_sysconfdir}/ssh/ssh_config
%dir %{_sysconfdir}/ssh/ssh_config.d
%{_bindir}/scp
%{_bindir}/sftp
%{_bindir}/ssh
%{_bindir}/ssh-add
%{_bindir}/ssh-agent
%{_bindir}/ssh-copy-id
%{_bindir}/ssh-keyscan
%{_libexecdir}/openssh/ssh-pkcs11-helper
%{_libexecdir}/openssh/ssh-sk-helper
%{_mandir}/man1/scp.1*
%{_mandir}/man1/sftp.1*
%{_mandir}/man1/ssh-add.1*
%{_mandir}/man1/ssh-agent.1*
%{_mandir}/man1/ssh-copy-id.1*
%{_mandir}/man1/ssh-keyscan.1*
%{_mandir}/man1/ssh.1*
%{_mandir}/man5/ssh_config.5*
%{_mandir}/man8/ssh-pkcs11-helper.8*
%{_mandir}/man8/ssh-sk-helper.8*

%files server
%attr(0711,root,root) %dir %{_localstatedir}/empty/sshd
%attr(0755,root,root) %{_sbindir}/sshd
%attr(0755,root,root) %{_libexecdir}/openssh/sftp-server
%attr(0755,root,root) %{_libexecdir}/openssh/sshd-keygen
%attr(0755,root,root) %{_libexecdir}/openssh/sshd-session
%attr(0755,root,root) %{_libexecdir}/openssh/sshd-auth
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/ssh/sshd_config
%dir %{_sysconfdir}/ssh/sshd_config.d
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/pam.d/sshd
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/sshd
%attr(0644,root,root) %{_unitdir}/sshd.service
%attr(0644,root,root) %{_unitdir}/sshd@.service
%attr(0644,root,root) %{_unitdir}/sshd.socket
%attr(0644,root,root) %{_unitdir}/sshd-keygen@.service
%attr(0644,root,root) %{_unitdir}/sshd-keygen.target
%attr(0644,root,root) %{_tmpfilesdir}/openssh.conf
%{_mandir}/man5/sshd_config.5*
%{_mandir}/man8/sshd.8*
%{_mandir}/man8/sftp-server.8*

%changelog
* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 10.5p1-1
- Initial package: upstream OpenSSH 10.5p1 for RHEL/CentOS 8, built from the
  portable tarball with the packaging skeleton (subpackage split, systemd units,
  sshd-keygen helper, /etc files) reused from Red Hat's el8 openssh-server.
  OpenSSH 10.5p1 requires OpenSSL >= 1.1.1, which el8 provides.
