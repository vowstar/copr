%global debug_package %{nil}

Name:       zellij
Version:    0.41.2
Release:    1%{?dist}
Summary:    A terminal workspace with batteries included.

License:    MIT
URL:        https://github.com/zellij-org/zellij
Source0:    %{url}/archive/refs/tags/v%{version}.tar.gz

BuildRequires: gcc
BuildRequires: python3-devel
BuildRequires: cmake
BuildRequires: openssl-devel
BuildRequires: perl-devel
BuildRequires: openssl-perl
%if 0%{?rhel} < 9
BuildRequires:  perl-interpreter
%else
BuildRequires:  perl-FindBin
%endif
BuildRequires: perl-IPC-Cmd

%description
Zellij is a workspace aimed at developers, ops-oriented people and anyone who loves the terminal. At its core, it is a terminal multiplexer (similar to tmux and screen), but this is merely its infrastructure layer. Zellij includes a layout system, and a plugin system allowing one to create plugins in any language that compiles to WebAssembly.


%prep
%autosetup -p1

curl https://sh.rustup.rs -sSf | sh -s -- --profile minimal -y

%install
export CARGO_PROFILE_RELEASE_BUILD_OVERRIDE_OPT_LEVEL=3
export PATH="$HOME/.cargo/bin:$PATH"
rustup default stable
cargo install --root=%{buildroot}%{_prefix} --path=.

rm -f %{buildroot}%{_prefix}/.crates.toml \
    %{buildroot}%{_prefix}/.crates2.json
strip --strip-all %{buildroot}%{_bindir}/*


%files
%license LICENSE.md
%doc README.md
%{_bindir}/zellij

