%define debug_package %{nil}
%define distname linux-wlan-ng-%{version}

Summary:	Utilities from the linux-wlan-ng project
Name:		prism2-utils
Version:	0.2.8
Release:	7
License:	MPL
Group:		System/Kernel and hardware
Url:		http://www.linux-wlan.com/linux-wlan/
Source0:	ftp://ftp.linux-wlan.org/pub/linux-wlan-ng/%{distname}.tar.bz2
Patch0:		linux-wlan-ng-0.2.8-udev.patch
Patch1:		linux-wlan-ng-0.2.8-rpmfiles.patch
Patch2:		linux-wlan-ng-0.2.8-disable_kernel_driver_build.patch
BuildRequires:	kernel-source-latest
BuildRequires:	kernel-devel
Provides:	linux-wlan-ng

%description
Tools for configuring the prism2 drivers for wireless network
cards using Intersil's Prism2/2.5/3 chipsets.

%prep
%setup -qn %{distname}
%apply_patches

# sed config.in for PCMCIA=n and TARGET_ROOT_ON_HOST=installdir
sed -e 's%PRISM2_PCMCIA=y%PRISM2_PCMCIA=n%g' config.in |\
sed -e s%TARGET_ROOT_ON_HOST=%TARGET_ROOT_ON_HOST=%{buildroot}%g > x
mv x config.in

make auto_config

# Mandriva has the drivers in the kernel, so we don't want to build
# them here, just the utils.

sed -e 's/p80211 prism2//g' src/Makefile > m
mv src/Makefile src/Makefile.prev
mv m src/Makefile

# want the config scripts for both fixed and cs versions to be
# installed for eventual use by drakconnect. hack the makefiles in etc.

sed -e 's%$(PRISM2_PLX)%y%g' etc/Makefile > m
mv m etc/Makefile
sed -e 's%$(PRISM2_PCMCIA)%y%g' etc/pcmcia/Makefile > m
mv m etc/pcmcia/Makefile

# fix man page location
perl -p -i -e 's|/usr/local/man|/usr/share/man||g' man/Makefile

%build
# use the headers from the Mandriva kernel
CFLAGS=-I/usr/src/linux/3rdparty/prism25/include make all

# make all

%install
# have to specify TARGET_PCMCIA_DIR since we want the config
# files even though we didn't build the driver.
TARGET_PCMCIA_DIR=%{buildroot}/etc/pcmcia make install
install -m 644 src/prism2/shared.prism2 %{buildroot}/etc/wlan/
install -d -m755 %{buildroot}/etc/udev/rules.d
install -m 644 etc/udev/rules.d/40-prism2.rules %{buildroot}/etc/udev/rules.d

# how did this get there?
rm -f %buildroot/etc/shared

%post
# disable wlan service by default, drakconnect should enable
# it when necessary.
chkconfig --del wlan

%files
%doc CHANGES COPYING FAQ LICENSE README THANKS TODO
%{_mandir}/man1/*
/sbin/*
%{_initrddir}/wlan
%{_sysconfdir}/wlan/shared
%config(noreplace) %{_sysconfdir}/pcmcia/wlan-ng
%config(noreplace) %{_sysconfdir}/pcmcia/wlan-ng.conf
%config(noreplace) %{_sysconfdir}/wlan/shared?*
%config(noreplace) %{_sysconfdir}/wlan/wlan-udev.sh
%config(noreplace) %{_sysconfdir}/wlan/wlan.conf
%attr(755,root,root) %config(noreplace) %{_sysconfdir}/wlan/wlancfg-DEFAULT
%config(noreplace) %{_sysconfdir}/udev/rules.d/40-prism2.rules

