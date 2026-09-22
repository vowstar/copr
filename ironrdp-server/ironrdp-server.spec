# IronRDP RDP server.
#
# Upstream `ironrdp-server` is a library; the only runnable server IronRDP
# publishes is the `server` example of the `ironrdp` meta crate (declared as
# `[[example]] name = "server"` with required-features cliprdr/connector/rdpsnd/
# server).  This package builds exactly that example, installs it as
# /usr/bin/ironrdp-server and runs it from a systemd unit, so that the crate
# linked at https://docs.rs/ironrdp-server/ (ironrdp-server 0.13.0, pulled in by
# the ironrdp 0.17.0 tarball) is usable as a system RDP service.
#
# The SELinux policy module in the -selinux subpackage is modelled on how Red
# Hat ships policy for its own RDP server (gnome-remote-desktop): a dedicated
# domain, a dedicated executable type, a dedicated state type and a dedicated
# TCP port type for the RDP port.  Unlike gnome-remote-desktop, whose module
# lives in the distribution's selinux-policy package, this module is shipped by
# the package itself, which is the model Fedora/EPEL use for xrdp (xrdp-selinux).
#
# Verified on Rocky Linux 8: builds with the rustup toolchain below (the crate
# MSRV is 1.89; el8's AppStream rust is older), the resulting server completes a
# real RDP session (HYBRID_EX/CredSSP + TLS) with the upstream IronRDP client,
# and the policy module compiles against selinux-policy-devel for both the
# targeted and mls variants.
#
# COPR chroots: the eight EL ones (el8/el9 families, rhel-8/9, epel-8/9), set via
#   copr-cli build-package -r epel-8-x86_64 -r rhel-8-x86_64 \
#     -r centos-stream-8-x86_64 -r centos-stream+epel-next-8-x86_64 \
#     -r epel-9-x86_64 -r rhel-9-x86_64 -r centos-stream-9-x86_64 \
#     -r centos-stream+epel-next-9-x86_64 --name ironrdp-server vowstar/eda
# The Fedora chroots cannot build it: rustls' default crypto provider aws-lc-sys
# (0.42.0, pinned by the crate's own Cargo.lock) compiles a feature-probe binary
# that Fedora's PIE/hardened-ld defaults refuse to link
#   /usr/bin/ld: relocation R_X86_64_32 against `.rodata' ...
#   /usr/bin/ld: failed to set dynamic section sizes: bad value
#   Failed to compile memcmp_invalid_stripped_check
# and its build script aborts instead of falling back.  Working around it would
# mean dropping the linker hardening for the whole package, so this package
# stays on the EL chroots, which is also where it is meant to be used.

%global crate          ironrdp
%global crate_ver      0.17.0
%global server_crate   ironrdp-server
# SELinux module name (D-Bus/RPM names cannot carry the dash)
%global selinux_module ironrdp_server
# system account the unit runs as (must match User= in %{name}.service)
%global daemon_user   ironrdp
# toolchain the build was tested with; upstream MSRV is 1.89
%global rust_version   1.98.1

# Cargo compiles the generated C dependencies (aws-lc-sys, zstd) inside
# CARGO_HOME, i.e. outside the rpmbuild BUILD directory, so the list of debug
# source files ends up empty and rpmbuild aborts the automatic debugsource
# subpackage with "Empty %%files file .../debugsourcefiles.list".  Undefining the
# macro (defined as 1 in redhat-rpm-config) disables that subpackage; the
# debuginfo subpackage is kept.
%undefine _debugsource_packages

# SELinux variants to build policy modules for, from /etc/selinux/config
%global selinux_types %(%{__awk} '/^#[[:space:]]*SELINUXTYPE=/,/^[^#]/ { if ($3 == "-") printf "%s ", $2 }' /etc/selinux/config 2>/dev/null)
%global selinux_variants %([ -z "%{selinux_types}" ] && echo mls targeted || echo %{selinux_types})

Name:           %{server_crate}
Version:        %{crate_ver}
Release:        1%{?dist}
Summary:        IronRDP RDP server

License:        MIT OR Apache-2.0
URL:            https://github.com/Devolutions/IronRDP
# The meta crate tarball is used because it carries examples/server.rs; it
# depends on ironrdp-server 0.13.0.
Source0:        https://static.crates.io/crates/%{crate}/%{crate}-%{version}.crate#/%{crate}-%{version}.tar.gz
Source1:        ironrdp_server.te
Source2:        ironrdp_server.fc
Source3:        %{name}.service
Source4:        %{name}.sysconfig

BuildRequires:  gcc-c++
BuildRequires:  make
# %%{_unitdir} and %%systemd_post/%%systemd_preun/%%systemd_postun_with_restart
# come from /usr/lib/rpm/macros.d/macros.systemd, which mock's minimal buildroot
# does not have: without this the el8/epel-8 chroots died with
#   error: File must begin with "/": %{_unitdir}/ironrdp-server.service
# On el8 that file belongs to the systemd package itself (el8 has no
# systemd-rpm-macros); on el9 and Fedora it is split out into systemd-rpm-macros.
# The %% above must stay escaped: rpm expands macros inside comments, and
# %%systemd_post expands to a multi-line shell fragment that breaks the parse.
%if 0%{?rhel} == 8
BuildRequires:  systemd
%else
BuildRequires:  systemd-rpm-macros
%endif
# aws-lc-sys (rustls' default crypto provider) is built from C sources
BuildRequires:  cmake
# the rdpsnd handler encodes OPUS through opus2/libopus
BuildRequires:  pkgconfig(opus)
BuildRequires:  curl
BuildRequires:  tar
BuildRequires:  checkpolicy
BuildRequires:  selinux-policy-devel

Requires(pre):  shadow-utils
Requires(post): systemd openssl
Requires(preun): systemd
Requires(postun): systemd
# loads the policy module and relabels the daemon
Recommends:     %{name}-selinux = %{version}-%{release}

%description
IronRDP is the Rust implementation of the Microsoft Remote Desktop Protocol
maintained by Devolutions.  This package provides a working RDP server built on
the ironrdp-server crate (0.13.0): it listens for RDP clients using Enhanced
RDP Security with TLS 1.2/1.3 and CredSSP (NLA), and serves bitmap display
updates, keyboard/mouse input, clipboard and sound channels.

The server hardware/software in this build is a development-oriented skeleton:
it streams generated bitmaps instead of a desktop session and authenticates a
single credential pair configured in /etc/sysconfig/ironrdp-server.

%package selinux
Summary:        SELinux policy for the IronRDP RDP server
Requires:       %{name} = %{version}-%{release}
%if "%{_selinux_policy_version}" != ""
Requires:       selinux-policy >= %{_selinux_policy_version}
%endif
Requires(post):   /usr/sbin/semodule
Requires(post):   /usr/sbin/semanage
Requires(post):   /sbin/restorecon
Requires(postun): /usr/sbin/semodule

%description selinux
SELinux policy module that runs the IronRDP RDP server in its own domain,
allows it to bind the dedicated RDP port type (TCP 3389) and to manage the TLS
identity under /var/lib/ironrdp-server.  The layout follows the policy Red Hat
ships for its own RDP server (gnome-remote-desktop) and the packaging follows
the xrdp-selinux subpackage.

%prep
%autosetup -n %{crate}-%{version}

# The upstream example prints "cargo run --example=server -- ..." as its usage;
# the installed command is ironrdp-server.
sed -i 's|cargo run --example=server --|%{name}|' examples/server.rs


%build
curl -sSf https://sh.rustup.rs | sh -s -- --profile minimal --default-toolchain none -y
export PATH="$HOME/.cargo/bin:$PATH"
rustup default %{rust_version}
rustc --version
cargo build --release --example server \
    --features server,cliprdr,connector,rdpsnd


%install
install -D -p -m 0755 target/release/examples/server %{buildroot}%{_bindir}/%{name}
install -D -p -m 0644 %{SOURCE3} %{buildroot}%{_unitdir}/%{name}.service
install -D -p -m 0600 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -d %{buildroot}%{_localstatedir}/lib/%{name}

# SELinux policy module, one .pp per SELinux variant
mkdir -p SELinux
cp %{SOURCE1} %{SOURCE2} SELinux/
for selinuxvariant in %{selinux_variants}
do
  %{__make} -C SELinux NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
  %{__mv} SELinux/%{selinux_module}.pp SELinux/%{selinux_module}.pp.${selinuxvariant}
  %{__make} -C SELinux NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done
for selinuxvariant in %{selinux_variants}
do
  install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
  install -p -m 0644 SELinux/%{selinux_module}.pp.${selinuxvariant} \
      %{buildroot}%{_datadir}/selinux/${selinuxvariant}/%{selinux_module}.pp
done


%pre
getent group %{daemon_user} >/dev/null || groupadd -r %{daemon_user}
getent passwd %{daemon_user} >/dev/null || \
    useradd -r -g %{daemon_user} -d %{_localstatedir}/lib/%{name} -s /sbin/nologin \
            -c "IronRDP RDP server" %{daemon_user}
exit 0


%post
# a TLS identity is mandatory for the RDP listener (TLS or TLS+CredSSP)
if [ ! -e %{_localstatedir}/lib/%{name}/cert.pem ] || [ ! -e %{_localstatedir}/lib/%{name}/key.pem ]; then
  /usr/bin/openssl req -x509 -nodes -newkey rsa:2048 \
      -keyout %{_localstatedir}/lib/%{name}/key.pem \
      -out %{_localstatedir}/lib/%{name}/cert.pem \
      -days 3650 -subj "/CN=$(hostname)" &>/dev/null || :
fi
%{__chmod} 0600 %{_localstatedir}/lib/%{name}/key.pem &>/dev/null || :
%{__chmod} 0644 %{_localstatedir}/lib/%{name}/cert.pem &>/dev/null || :
chown -R %{daemon_user}:%{daemon_user} %{_localstatedir}/lib/%{name} &>/dev/null || :

%systemd_post %{name}.service


%preun
%systemd_preun %{name}.service


%postun
%systemd_postun_with_restart %{name}.service


%post selinux
for selinuxvariant in %{selinux_variants}
do
  /usr/sbin/semodule -s ${selinuxvariant} -i \
      %{_datadir}/selinux/${selinuxvariant}/%{selinux_module}.pp &> /dev/null || :
done
# Assign TCP 3389 to the port type declared by the module.  A module cannot carry
# a portcon (base policy statement), so this is done here; it also means that on a
# system whose own policy already gives 3389 to another RDP server
# (gnome_remote_desktop_port_t on Fedora/RHEL 10) the -a below fails and -m moves
# the port to this package's type -- two RDP servers cannot share the port anyway.
/usr/sbin/semanage port -a -t %{selinux_module}_port_t -p tcp 3389 &> /dev/null \
    || /usr/sbin/semanage port -m -t %{selinux_module}_port_t -p tcp 3389 &> /dev/null || :
# the .fc labels the executable and the state directory
if [ -x /usr/sbin/selinuxenabled ] && /usr/sbin/selinuxenabled; then
  /sbin/restorecon -R %{_bindir}/%{name} %{_localstatedir}/lib/%{name} &> /dev/null || :
fi


%postun selinux
if [ $1 -eq 0 ] ; then
  for selinuxvariant in %{selinux_variants}
  do
    /usr/sbin/semodule -s ${selinuxvariant} -r %{selinux_module} &> /dev/null || :
  done
fi


%files
%license LICENSE-MIT LICENSE-APACHE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%config(noreplace) %attr(0600,root,root) %{_sysconfdir}/sysconfig/%{name}
%dir %attr(0700,%{daemon_user},%{daemon_user}) %{_localstatedir}/lib/%{name}


%files selinux
%doc SELinux/%{selinux_module}.te
%{_datadir}/selinux/*/%{selinux_module}.pp


%changelog
* Mon Sep 21 2026 vowstar <vowstar@gmail.com> - 0.17.0-1
- Initial package: IronRDP 0.17.0 server (ironrdp-server 0.13.0) as a systemd
  service, with an xrdp-style -selinux subpackage modelled on the policy Red Hat
  ships for gnome-remote-desktop
