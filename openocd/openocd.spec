%global pkgvers 0
%global scdate0 20241009
%global schash0 30c3d077f281876286a7aa37afbd411d4bd1667e
%global branch0 master
%global source0 https://github.com/openocd-org/openocd.git

%global sshort0 %{expand:%%{lua:print(('%{schash0}'):sub(1,8))}}

Name:           openocd
Version:        %(curl -s https://raw.githubusercontent.com/openocd-org/openocd/%{schash0}/configure.ac | grep "\[openocd\]" | cut -d'[' -f3 | cut -d']' -f1 | sed 's|[+,-,a-z]||g')
Release:        %{scdate0}.%{pkgvers}.git%{sshort0}%{?dist}
Summary:        Debugging, in-system programming and boundary-scan testing for embedded devices
License:        GPLv2

URL:            https://openocd.org

BuildRequires:  gcc make libtool git
BuildRequires:  chrpath libusbx-devel jimtcl-devel >= 0.78
BuildRequires:  libusb1-devel texinfo libjaylink-devel >= 0.2
%if ! 0%{?rhel} == 9
BuildRequires:  stlink-devel
%endif
%if 0%{?fedora}
BuildRequires:  sdcc
%endif
%if 0%{?epel}
BuildRequires:  capstone-devel libftdi-devel hidapi-devel libgpiod-devel < 2
%endif
%if 0%{?fedora}
BuildRequires:  capstone-devel libftdi-devel hidapi-devel
%endif

%description
The Open On-Chip Debugger (OpenOCD) provides debugging, in-system programming 
and boundary-scan testing for embedded devices. Various different boards, 
targets, and interfaces are supported to ease development time.

Install OpenOCD if you are looking for an open source solution for hardware 
debugging.

%prep
%setup -T -c -n %{name}
git clone --depth 1 -n -b %{branch0} %{source0} .
git fetch --depth 1 origin %{schash0}
git reset --hard %{schash0}
git log --format=fuller
# fix udev rules
sed -i 's/MODE=.*/TAG+="uaccess"/' contrib/60-openocd.rules
# fix header
sed -i '1i #include <stdio.h>' src/helper/jim-nvp.c
sed -i '1i #include <stdio.h>' src/helper/configuration.h


%build
./bootstrap nosubmodule
rm -rf jimtcl
rm -rf libjaylink
%if 0%{?fedora}
pushd src/jtag/drivers/OpenULINK
rm -f ulink_firmware.hex
make PREFIX=sdcc hex
popd
%endif
%configure \
  --disable-werror \
  --enable-static \
  --disable-shared \
  --enable-dummy \
  --enable-ftdi \
%if 0%{?rhel} == 9
  --disable-stlink \
%else
  --enable-stlink \
%endif
  --enable-ti-icdi \
  --enable-ulink \
  --enable-usb-blaster-2 \
  --enable-ft232r \
  --enable-vsllink \
  --enable-xds110 \
%if (0%{?epel} || 0%{?fedora})
  --enable-cmsis-dap-v2 \
%else
  --disable-cmsis-dap-v2 \
%endif
  --enable-osbdm \
  --enable-opendous \
  --enable-aice \
  --enable-usbprog \
  --enable-rlink \
  --enable-armjtagew \
%if (0%{?epel} || 0%{?fedora})
  --enable-cmsis-dap \
%else
  --disable-cmsis-dap \
%endif
  --enable-nulink \
  --enable-kitprog \
  --enable-usb-blaster \
  --enable-presto \
  --enable-openjtag \
  --enable-jlink \
  --enable-parport \
  --enable-jtag_vpi \
  --enable-jtag_dpi \
  --enable-ioutil \
  --enable-amtjtagaccel \
  --enable-ep39xx \
  --enable-at91rm9200 \
  --enable-gw16012 \
  --enable-oocd_trace \
  --enable-buspirate \
  --enable-sysfsgpio \
  --enable-linuxgpiod \
  --enable-xlnx-pcie-xvc \
  --enable-remote-bitbang \
  --disable-internal-jimtcl \
  --disable-internal-libjaylink \
  --disable-doxygen-html \
  CROSS=
%make_build

%install
%make_install
rm -f %{buildroot}/%{_infodir}/dir
rm -f %{buildroot}/%{_libdir}/libopenocd.*
rm -rf %{buildroot}/%{_datadir}/%{name}/contrib
mkdir -p %{buildroot}/%{_prefix}/lib/udev/rules.d/
install -p -m 644 contrib/60-openocd.rules %{buildroot}/%{_prefix}/lib/udev/rules.d/60-openocd.rules
chrpath --delete %{buildroot}/%{_bindir}/openocd

%files
%license COPYING
%doc AUTHORS ChangeLog NEWS* NEWTAPS README TODO
%{_datadir}/%{name}/angie
%{_datadir}/%{name}/scripts
%{_datadir}/%{name}/OpenULINK/ulink_firmware.hex
%{_bindir}/%{name}
%{_prefix}/lib/udev/rules.d/60-openocd.rules
# doc
%{_infodir}/%{name}.info*.gz
%{_mandir}/man1/*

%changelog
* Tue Aug 17 2021 Cristian Balint <cristian.balint@gmail.com>
- update to git releases

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.0-1.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild
