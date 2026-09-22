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
# Feature set: everything RHEL 9 enables that is worth having here -- PAM,
# SELinux, audit, systemd, GSSAPI/Kerberos (--with-kerberos5), FIDO/U2F security
# keys (--with-security-key-builtin), libedit for interactive history,
# PKCS#11/engine support, IPv4-first, a vendor patchlevel string.  The two RHEL
# options deliberately left out are --with-rsh (rsh/rlogin clients, obsolete) and
# --enable-dsa-keys (upstream removed DSA in 10.0 and it is weak anyway).
#
# The crypto-policies back-end file is written for RHEL's patched openssh and
# contains items an upstream build does not implement: GSSAPIKexAlgorithms (from
# RHEL's GSSAPI-key-exchange patch -- upstream has GSSAPI authentication but no
# GSSAPI key exchange at all, --with-kerberos5 does not provide that option) and,
# in the newer policies, algorithm names such as mlkem1024nistp384-sha384
# (upstream 10.5 implements ML-KEM-768 only).  An unknown -o option or algorithm
# name given on the command line is fatal, unlike one in the config file, so the
# policy is audited against the built binary by
# %{_libexecdir}/openssh/crypto-policy-args before it reaches sshd: unsupported
# options and names are dropped and logged, and the daemon still starts when the
# host's policy is newer than this build.  FIDO likewise must match the policy:
# crypto-policies lists sk-ecdsa-sha2-nistp256@openssh.com and
# sk-ssh-ed25519@openssh.com among the accepted host key / pubkey / CA
# signature algorithms.
#
# Build (as vowstar, from ~/rpmbuild):  rpmbuild -bb SPECS/openssh.spec
# Install (as root):                    dnf upgrade RPMS/x86_64/openssh-*.rpm

%global openssh_ver 10.5p1

Name:           openssh
Version:        %{openssh_ver}
Release:        6%{?dist}
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
# The crypto-policies audit and the service drop-in that routes the unit through
# it (see the comment at the top of this file).
Source10:       openssh-crypto-policy
Source11:       sshd-service-crypto-policy.conf
# Red Hat's el8 sshd_config, for the reason spelled out in %install.
Source12:       sshd_config

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  groff
BuildRequires:  openssl-devel
BuildRequires:  zlib-devel
BuildRequires:  pam-devel
BuildRequires:  libfido2-devel
BuildRequires:  libedit-devel
BuildRequires:  ncurses-devel
BuildRequires:  p11-kit-devel
# GSSAPI (Kerberos 5) support.  Not optional on el8/el9 in practice: the
# distribution's crypto-policies feed sshd a command line of -o options
# (/etc/crypto-policies/back-ends/opensshserver.config, expanded by the unit
# into $CRYPTO_POLICY) that includes -oGSSAPIKexAlgorithms=...  An sshd built
# without krb5 does not know that option, and an unknown option passed with -o
# is fatal -- only a warning when it comes from the config file:
#   command-line: line 0: Bad configuration option: GSSAPIKexAlgorithms
#   sshd.service: Main process exited, code=exited, status=1/FAILURE
# so the daemon never starts and systemd retries forever.  Building with
# krb5-devel also removes the GSSAPIAuthentication / GSSAPICleanupCredentials
# "Unsupported option" warnings from sshd_config.
BuildRequires:  krb5-devel
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
Requires:       xauth
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
    --with-kerberos5 \
    --with-security-key-builtin=yes \
    --with-libedit \
    --with-default-pkcs11-provider=yes \
%if 0%{?rhel} == 8
    --with-ssl-engine \
%endif
    --with-ipv4-default \
    --enable-vendor-patchlevel=eda \
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
install -p -m 0755 %{SOURCE10} %{buildroot}%{_libexecdir}/openssh/crypto-policy-args
install -d -m 0755 %{buildroot}%{_unitdir}/sshd.service.d
install -p -m 0644 %{SOURCE11} %{buildroot}%{_unitdir}/sshd.service.d/10-crypto-policy.conf
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
# ... and ship Red Hat's sshd_config rather than upstream's.  Upstream's file has
# its defaults commented out, and RPM replaces an unmodified %config file, so on
# a host upgraded from the distribution's openssh upstream's file silently drops
# UsePAM yes, PermitRootLogin yes, X11Forwarding yes, GSSAPIAuthentication yes,
# SyslogFacility AUTHPRIV and the AcceptEnv locale forwarding -- PAM off is not
# a cosmetic change.  This file is the distribution's, and this build accepts it
# unchanged (sshd -t passes with it).
install -p -m 0600 %{SOURCE12} %{buildroot}%{_sysconfdir}/ssh/sshd_config

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
# Host keys left over from the distribution's openssh are 0640 root:ssh_keys
# (Red Hat's keyperm patch and its sshd-keygen), and this build has no such
# patch: upstream's sshd refuses a group readable private key and then exits with
# "no hostkeys available", so the daemon would not come back up after this
# upgrade.  Normalize them now, and sshd.tmpfiles keeps them that way on every
# boot.  Both implementations accept 0600 root:root.
for key in %{_sysconfdir}/ssh/ssh_host_*_key; do
    [ -f "$key" ] || continue
    chown root:root "$key" 2>/dev/null || :
    chmod 0600 "$key" 2>/dev/null || :
done

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
%attr(0755,root,root) %{_libexecdir}/openssh/crypto-policy-args
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/ssh/sshd_config
%dir %{_sysconfdir}/ssh/sshd_config.d
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/pam.d/sshd
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/sysconfig/sshd
%attr(0644,root,root) %{_unitdir}/sshd.service
%attr(0644,root,root) %{_unitdir}/sshd@.service
%attr(0644,root,root) %{_unitdir}/sshd.socket
%attr(0644,root,root) %{_unitdir}/sshd-keygen@.service
%attr(0644,root,root) %{_unitdir}/sshd-keygen.target
%dir %{_unitdir}/sshd.service.d
%attr(0644,root,root) %{_unitdir}/sshd.service.d/10-crypto-policy.conf
%attr(0644,root,root) %{_tmpfilesdir}/openssh.conf
%{_mandir}/man5/sshd_config.5*
%{_mandir}/man8/sshd.8*
%{_mandir}/man8/sftp-server.8*

%changelog
* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 10.5p1-6
- Ship Red Hat's el8 sshd_config instead of upstream's.  RPM replaces an
  unmodified %config file, and upstream's sshd_config has its defaults commented
  out, so the upgrade silently dropped UsePAM yes, PermitRootLogin yes,
  X11Forwarding yes, GSSAPIAuthentication yes, SyslogFacility AUTHPRIV and the
  AcceptEnv locale forwarding that the distribution's file sets -- PAM off is not
  a cosmetic change.  Found by diffing the distribution's file against the one
  the upgrade left on a real systemd container; this build accepts the
  distribution's file as is (sshd -t passes).

* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 10.5p1-5
- Normalize host keys left over from the distribution to 0600 root:root, in
  %post and through sshd.tmpfiles.  Red Hat's sshd-keygen creates them
  0640 root:ssh_keys for its keyperm patch, which this build does not carry, and
  upstream's sshd refuses a group readable private key: on a host upgraded from
  the distribution's openssh the daemon could not start at all --
    Permissions 0640 for '/etc/ssh/ssh_host_ed25519_key' are too open.
    sshd: no hostkeys available -- exiting.
    sshd.service: Main process exited, code=exited, status=1/FAILURE
  0600 root:root is accepted by both implementations.  Found by upgrading a real
  systemd container from the distribution's 8.0p1 to 10.5p1-4; with the keys
  fixed the same unit starts and listens on 22, with the crypto policies audited
  by crypto-policy-args in the journal.

* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 10.5p1-4
- Audit the system crypto policies against the built binary instead of handing
  them to sshd verbatim.  GSSAPIKexAlgorithms is not an upstream option at all:
  it belongs to RHEL's GSSAPI-key-exchange patch, a feature upstream does not
  have (GSSAPIKeyExchange appears nowhere in the 10.5 tree), so --with-kerberos5
  from -2 does not make sshd accept it and the daemon still refused to start.
  The newer policies also carry kex names this build does not implement
  (mlkem1024nistp384-sha384; 10.5 has ML-KEM-768 only).  Both are dropped now,
  each with a journal line, while the rest of the policy -- the mlkem768 kexes
  included -- is applied unchanged.
- The audit is %{_libexecdir}/openssh/crypto-policy-args plus a drop-in for
  sshd.service, which asks the daemon itself (sshd -T) what it supports, so the
  answer cannot drift from the binary that runs.  It prints no policy options at
  all if it cannot decide, so a policy newer than this build can never keep the
  daemon from starting.

* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 10.5p1-3
- Enable the rest of the feature set RHEL 9 builds: FIDO/U2F security keys
  (--with-security-key-builtin, libfido2-devel), libedit, PKCS#11
  (--with-default-pkcs11-provider, --with-ssl-engine), IPv4-first and a vendor
  patchlevel string; add the xauth runtime requirement for X11 forwarding.
  crypto-policies lists sk-ecdsa-sha2-nistp256@openssh.com and
  sk-ssh-ed25519@openssh.com among the accepted algorithms, so a build without
  FIDO cannot accept the distribution's own policy.

* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 10.5p1-2
- Build with krb5-devel and --with-kerberos5.  Without GSSAPI the daemon does
  not understand the -oGSSAPIKexAlgorithms=... option that the RHEL 8/9 crypto
  policies pass on the sshd command line, an unknown option given with -o is
  fatal (unlike one in the config file), and the service never came up:
    command-line: line 0: Bad configuration option: GSSAPIKexAlgorithms
    sshd.service: Main process exited, code=exited, status=1/FAILURE

* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 10.5p1-1
- Initial package: upstream OpenSSH 10.5p1 for RHEL/CentOS 8, built from the
  portable tarball with the packaging skeleton (subpackage split, systemd units,
  sshd-keygen helper, /etc files) reused from Red Hat's el8 openssh-server.
  OpenSSH 10.5p1 requires OpenSSL >= 1.1.1, which el8 provides.
