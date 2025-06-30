Name:           pandoc
Version:        3.7.0.2
Release:        1%{?dist}
Summary:        Pandoc is a universal document converter. It can convert between various markup formats including Markdown, HTML, LaTeX, PDF, and more.

License:        GPLv2+
URL:            https://pandoc.org/
Source0:        https://github.com/jgm/pandoc/releases/download/%{version}/pandoc-%{version}-linux-amd64.tar.gz

ExclusiveArch:  x86_64
# disable debug package (only install pre-compiled binary)
%global debug_package %{nil}

Requires:       glibc >= 2.17
BuildRequires:  gzip

%description
Pandoc is a universal document converter. It can convert between various
markup formats including Markdown, HTML, LaTeX, PDF, and more.

%prep
%setup -q

%build
# pre-compiled package, no build

%check
# no check

%install
# install executable
install -d %{buildroot}%{_bindir}
install -m 755 bin/pandoc %{buildroot}%{_bindir}/pandoc
ln -sf pandoc %{buildroot}%{_bindir}/pandoc-server
ln -sf pandoc %{buildroot}%{_bindir}/pandoc-lua

# install man
install -d %{buildroot}%{_mandir}/man1
install -m 644 share/man/man1/*.gz %{buildroot}%{_mandir}/man1/

%files
%{_bindir}/pandoc
%{_bindir}/pandoc-server
%{_bindir}/pandoc-lua
%{_mandir}/man1/pandoc.1.gz
%{_mandir}/man1/pandoc-server.1.gz
%{_mandir}/man1/pandoc-lua.1.gz
