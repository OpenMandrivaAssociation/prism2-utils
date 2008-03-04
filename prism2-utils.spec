%define name 	prism2-utils
%define version 0.2.1
%define pretag	pre26
%define release %mkrel 0.%{pretag}.5

Summary: 	Utilities from the linux-wlan-ng project
Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
URL:		http://www.linux-wlan.com/linux-wlan/
Source0: 	linux-wlan-ng-%{version}-%{pretag}.tar.bz2
Patch0:		linux-wlan-ng-0.2.1pre21.I-Gate-11M.patch
Patch1:		linux-wlan-ng-0.2.1-pre26-ignore-rpmfiles.patch
License: 	MPL
Group: 		System/Kernel and hardware
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires: 	kernel-source-latest
Provides:	linux-wlan-ng

%description
Tools for configuring the prism2 drivers for wireless network
cards using Intersil's Prism2/2.5/3 chipsets.

%prep
%setup -q -n linux-wlan-ng-%{version}-%{pretag}

%patch0 -p1 -b .I-Gate-11M
%patch1 -p1 -b .rpmfiles

# sed config.in for PCMCIA=n and TARGET_ROOT_ON_HOST=installdir
sed -e 's%PRISM2_PCMCIA=y%PRISM2_PCMCIA=n%g' config.in |\
sed -e s%TARGET_ROOT_ON_HOST=%TARGET_ROOT_ON_HOST=$RPM_BUILD_ROOT%g > x
mv x config.in

perl -pi -e 's|#LINUX_SRC|LINUX_SRC|g' config.in

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
rm -rf $RPM_BUILD_ROOT
# have to specify TARGET_PCMCIA_DIR since we want the config
# files even though we didn't build the driver.
install -d -m755 $RPM_BUILD_ROOT/etc/hotplug
TARGET_PCMCIA_DIR=$RPM_BUILD_ROOT/etc/pcmcia make install
install -m 644 src/prism2/shared.prism2 $RPM_BUILD_ROOT/etc/wlan/

# how did this get there?
rm -f %buildroot/etc/shared

%post
# disable wlan service by default, drakconnect should enable
# it when necessary.
chkconfig --del wlan

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc CHANGES COPYING FAQ LICENSE README THANKS TODO
%_mandir/man1/*
/sbin/*
%config(noreplace) %_initrddir/wlan
%config %_sysconfdir/wlan/shared
%config(noreplace) %_sysconfdir/pcmcia/wlan-ng
%config(noreplace) %_sysconfdir/pcmcia/wlan-ng.conf
%config(noreplace) %_sysconfdir/wlan/shared*
%config(noreplace) %_sysconfdir/wlan/wlan.conf
%attr(755,root,root) %config(noreplace) %_sysconfdir/wlan/wlancfg-DEFAULT
%attr(755,root,root) %config(noreplace) %_sysconfdir/hotplug/wlan.agent


