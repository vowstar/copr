Name:       pandoc
Version:    3.7.0.2
Release:    1%{?dist}
Summary:    Universal document converter
License:    GPLv2+
URL:        https://pandoc.org/
Source0:    https://github.com/jgm/pandoc/releases/download/%{version}/pandoc-%{version}-linux-amd64.tar.gz
BuildArch:  x86_64

%description
Pandoc is a universal document converter. It can convert between
various markup formats including Markdown, HTML, LaTeX, PDF, and more.

%prep
%autosetup -c -T

%build

%check

%install
# Install binary
install -d %buildroot%_bindir
install -m 755 bin/pandoc %buildroot%_bindir/

# Create symbolic links
ln -sf pandoc %buildroot%_bindir/pandoc-server
ln -sf pandoc %buildroot%_bindir/pandoc-lua

# Install man pages
install -d %buildroot%_mandir/man1
install -m 644 share/man/man1/*.gz %buildroot%_mandir/man1/

%files
%_bindir/pandoc
%_bindir/pandoc-server
%_bindir/pandoc-lua
%_mandir/man1/pandoc.1.gz
%_mandir/man1/pandoc-server.1.gz
%_mandir/man1/pandoc-lua.1.gz
