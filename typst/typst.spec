%global debug_package %{nil}

Name:       typst
Version:    0.13.1
Release:    1%{?dist}
Summary:    A new markup-based typesetting system that is powerful and easy to learn.

License:    Apache-2.0
URL:        https://github.com/typst/typst
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
Typst is a new markup-based typesetting system that is designed to be as powerful as LaTeX while being much easier to learn and use.


%prep
%autosetup -p1

curl https://sh.rustup.rs -sSf | sh -s -- --profile minimal --default-toolchain none  -y

%build
export CARGO_PROFILE_RELEASE_BUILD_OVERRIDE_OPT_LEVEL=3
export PATH="$HOME/.cargo/bin:$PATH"
$HOME/.cargo/bin/rustup default 1.75.0
$HOME/.cargo/bin/cargo build -p typst-cli --release --all-features --locked

%install

install -d -m 0755 %{buildroot}%{_bindir}
install -m 0755 target/release/typst %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
