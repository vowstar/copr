%global srcdir verible-v0.0-4294-gc1d8f5e8

Name:           verible
Version:        0.0.4294.gc1d8f5e8
Release:        1%{?dist}
Summary:        Suite of SystemVerilog developer tools
License:        Apache
URL:            https://chipsalliance.github.io/verible/
Source0:        https://github.com/chipsalliance/verible/releases/download/v0.0-4294-gc1d8f5e8/verible-v0.0-4294-gc1d8f5e8-linux-static-x86_64.tar.gz

ExclusiveArch:  x86_64

# upstream ships pre-compiled static binaries, there is nothing to build
%global debug_package %{nil}
# no debuginfo subpackage, so no build-id link farm is needed
%global _build_id_links none

BuildRequires:  gzip

%description
Verible is a suite of SystemVerilog developer tools,
including a parser, style-linter, and formatter.


%prep
%setup -q -n %{srcdir}


%build
# pre-compiled package, no build


%check
# smoke test the shipped payload
bin/verible-verilog-lint --version


%install
install -d %{buildroot}%{_bindir}
install -m 755 bin/* %{buildroot}%{_bindir}/


%files
%{_bindir}/verible-patch-tool
%{_bindir}/verible-verilog-diff
%{_bindir}/verible-verilog-format
%{_bindir}/verible-verilog-kythe-extractor
%{_bindir}/verible-verilog-kythe-kzip-writer
%{_bindir}/verible-verilog-lint
%{_bindir}/verible-verilog-ls
%{_bindir}/verible-verilog-obfuscate
%{_bindir}/verible-verilog-preprocessor
%{_bindir}/verible-verilog-project
%{_bindir}/verible-verilog-syntax


%changelog
* Tue Sep 22 2026 Cristian Balint <cristian.balint@gmail.com>
- repackage upstream v0.0-4294-gc1d8f5e8 prebuilt static x86_64 binaries
