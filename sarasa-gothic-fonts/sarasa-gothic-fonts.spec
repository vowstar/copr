Name:       sarasa-gothic-fonts
Version:    1.0.31
Release:    1%{?dist}
Summary:    a CJK composite font
License:    OFL-1.1
URL:        https://github.com/be5invis/Sarasa-Gothic
Source0:    https://github.com/be5invis/Sarasa-Gothic/releases/download/v1.0.31/Sarasa-TTC-1.0.31.zip
BuildArch:  noarch

%description
This is SARASA GOTHIC, a CJK composite font based on
Inter, Iosevka and Source Han Sans.

%prep
%autosetup -c -T
unzip -qq %{SOURCE0}

%build

%check

%install
install -d %buildroot%_datadir/fonts/%name
install -m 644 *.ttc %buildroot%_datadir/fonts/%name

%files
%_datadir/fonts/%name/
