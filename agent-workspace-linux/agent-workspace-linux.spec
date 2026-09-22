# agent-workspace-linux: a Rust MCP server that hands an AI agent its own hidden
# X11 desktop (Xvfb, a window manager, its own browser and clipboard) instead of
# driving the real one.  Built from source here, like zellij.spec in this repo,
# with the Rust toolchain bootstrapped by rustup.
#
# Why not repackage the prebuilt GitHub Release asset: those binaries are linked
# on ubuntu-latest and need GLIBC_2.39 plus libm GLIBC_2.35, so they abort with
# "version `GLIBC_2.39' not found" on el8 (glibc 2.28) and el9 (glibc 2.34); they
# only run on Fedora 40 and newer.  A local build links the chroot glibc, which
# is what every chroot this project targets needs.
#
# The build wants git and network access on top of the rustup bootstrap: two
# dependencies (gpui and gpui_platform, out of the zed-editor repository) exist
# only as git dependencies, pinned by the upstream Cargo.lock to commit 9d272b03,
# and that repository's rust-toolchain.toml pins 1.98.1, so the toolchain below
# is pinned to the same version and no distro Rust is new enough.
#
# Build (as vowstar, from ~/rpmbuild):  rpmbuild -bb SPECS/agent-workspace-linux.spec
# Install (as root):                    rpm -Uvh RPMS/x86_64/agent-workspace-linux-0.3.3-1.el8.x86_64.rpm

%global debug_package %{nil}

Name:           agent-workspace-linux
Version:        0.3.3
Release:        1%{?dist}
Summary:        Isolated Linux desktop workspaces for AI agents
License:        MIT
URL:            https://github.com/agent-sh/agent-workspace-linux
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  pkgconfig
BuildRequires:  git
BuildRequires:  curl
BuildRequires:  fontconfig-devel
BuildRequires:  freetype-devel
BuildRequires:  openssl-devel
BuildRequires:  libX11-devel
BuildRequires:  libxcb-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  libxkbcommon-x11-devel
BuildRequires:  wayland-devel
BuildRequires:  xcb-util-devel
BuildRequires:  xcb-util-image-devel
BuildRequires:  xcb-util-keysyms-devel
BuildRequires:  xcb-util-renderutil-devel
BuildRequires:  xcb-util-wm-devel

# Without an X server, the X utilities the workspace shells out to, and the
# bubblewrap sandbox helper the tool cannot do its job at all; all three sit in
# the base repositories of both Enterprise Linux generations.
Requires:       xorg-x11-server-Xvfb
Requires:       xorg-x11-utils
Requires:       bubblewrap
# The window manager, input, clipboard and screenshot tools are EPEL-only on
# Enterprise Linux, so they stay weak dependencies: dnf still installs them by
# default, yet the package remains installable on rhel and centos-stream
# chroots that carry no EPEL.
Recommends:     openbox
Recommends:     xdotool
Recommends:     xclip
Recommends:     ImageMagick

%description
agent-workspace-linux gives an AI agent a desktop of its own instead of taking
over yours.  It runs a hidden Xvfb display with its own window manager,
applications, clipboard and browser, and exposes them over MCP (stdio) so an
agent host such as Claude Code or Codex can launch apps, type, click,
screenshot and browse inside that workspace, while a small floating viewer lets
a human watch and pause it.  Optional permission ceilings (network, mounts, app
allowlist) are enforced by flag or environment variable for the life of the
process.

%prep
%setup -q

curl https://sh.rustup.rs -sSf | sh -s -- --profile minimal --default-toolchain none -y
export PATH="$HOME/.cargo/bin:$PATH"
rustup default 1.98.1

%build
export PATH="$HOME/.cargo/bin:$PATH"
cargo build --locked --release

%install
install -d %{buildroot}%{_bindir}
install -m 0755 target/release/%{name} %{buildroot}%{_bindir}/%{name}
strip --strip-all %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md
%doc skills/agent-workspace-linux/SKILL.md
%{_bindir}/%{name}

%changelog
* Tue Sep 22 2026 vowstar <vowstar@gmail.com> - 0.3.3-1
- Initial package, built from the v0.3.3 release tarball with the pinned
  rustup toolchain 1.98.1 that the gpui dependency tree requires
- Source build instead of the upstream prebuilt asset: the published binaries
  need GLIBC_2.39 and cannot run on el8 or el9
