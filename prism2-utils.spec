%define name 	prism2-utils
%define version 0.2.8
%define pretag	0
%if %pretag
%define release %mkrel 0.%{pretag}.9
%define distname linux-wlan-ng-%{version}-%{pretag}
%else
%define release %mkrel 6
%define distname linux-wlan-ng-%{version}
%endif

Summary: 	Utilities from the linux-wlan-ng project
Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
URL:		http://www.linux-wlan.com/linux-wlan/
Source0: 	ftp://ftp.linux-wlan.org/pub/linux-wlan-ng/%{distname}.tar.bz2
Patch0:		linux-wlan-ng-0.2.8-udev.patch
Patch1:		linux-wlan-ng-0.2.8-rpmfiles.patch
Patch2:		linux-wlan-ng-0.2.8-disable_kernel_driver_build.patch
License: 	MPL
Group: 		System/Kernel and hardware
BuildRequires: 	kernel-source-latest
BuildRequires: 	kernel-devel
Provides:	linux-wlan-ng
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Tools for configuring the prism2 drivers for wireless network
cards using Intersil's Prism2/2.5/3 chipsets.

%prep
%setup -q -n %{distname}
%patch0 -p1 -b .udev
%patch1 -p1 -b .rpmfiles
%patch2 -p1 -b .disable_kernel_driver_build

# sed config.in for PCMCIA=n and TARGET_ROOT_ON_HOST=installdir
sed -e 's%PRISM2_PCMCIA=y%PRISM2_PCMCIA=n%g' config.in |\
sed -e s%TARGET_ROOT_ON_HOST=%TARGET_ROOT_ON_HOST=$RPM_BUILD_ROOT%g > x
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
rm -rf $RPM_BUILD_ROOT
# have to specify TARGET_PCMCIA_DIR since we want the config
# files even though we didn't build the driver.
TARGET_PCMCIA_DIR=$RPM_BUILD_ROOT/etc/pcmcia make install
install -m 644 src/prism2/shared.prism2 $RPM_BUILD_ROOT/etc/wlan/
install -d -m755 $RPM_BUILD_ROOT/etc/udev/rules.d
install -m 644 etc/udev/rules.d/40-prism2.rules $RPM_BUILD_ROOT/etc/udev/rules.d

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
%_initrddir/wlan
%_sysconfdir/wlan/shared
%config(noreplace) %_sysconfdir/pcmcia/wlan-ng
%config(noreplace) %_sysconfdir/pcmcia/wlan-ng.conf
%config(noreplace) %_sysconfdir/wlan/shared?*
%config(noreplace) %_sysconfdir/wlan/wlan-udev.sh
%config(noreplace) %_sysconfdir/wlan/wlan.conf
%attr(755,root,root) %config(noreplace) %_sysconfdir/wlan/wlancfg-DEFAULT
%config(noreplace) %{_sysconfdir}/udev/rules.d/40-prism2.rules


%changelog
* Thu May 05 2011 Oden Eriksson <oeriksson@mandriva.com> 0.2.8-6mdv2011.0
+ Revision: 667846
- mass rebuild

* Fri Dec 03 2010 Oden Eriksson <oeriksson@mandriva.com> 0.2.8-5mdv2011.0
+ Revision: 607210
- rebuild

* Wed Feb 03 2010 Frederic Crozat <fcrozat@mandriva.com> 0.2.8-4mdv2010.1
+ Revision: 500305
- Fix obsolete syntax in udev rules

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 0.2.8-3mdv2010.0
+ Revision: 426781
- rebuild

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 0.2.8-3mdv2009.1
+ Revision: 351611
- rebuild

* Wed Aug 20 2008 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 0.2.8-3mdv2009.0
+ Revision: 274399
- Fix build with not prepared kernel-source package.

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

* Fri Mar 07 2008 Olivier Blin <oblin@mandriva.com> 0.2.8-1mdv2008.1
+ Revision: 181235
- always start interfaces in initscript, and do not start them at boot with udev rules (could hang)
- do not install unused hotplug agent
- package udev rule
- do not mark /etc/wlan/shared and initscript as config files
- do not package /etc/wlan/shared twice
- package wlan-udev.sh
- rediff rpmfiles patch
- drop I-Gate-11M patch (merged upstream)
- 0.2.8 (really commit tarballs)
- 0.2.8
- restore BuildRoot

  + Oden Eriksson <oeriksson@mandriva.com>
    - fix build deps (kernel-devel)
    - rebuild

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Thu Sep 20 2007 Olivier Blin <oblin@mandriva.com> 0.2.1-0.pre26.4mdv2008.0
+ Revision: 91491
- do not package devel doc

  + Thierry Vignaud <tv@mandriva.org>
    - s/Mandrake/Mandriva/


* Sat Mar 17 2007 Olivier Blin <oblin@mandriva.com> 0.2.1-0.pre26.3mdv2007.1
+ Revision: 145458
- rebuild
- Import prism2-utils

* Sat Feb 12 2005 Olivier Blin <oblin@mandrakesoft.com> 0.2.1-0.pre26.2mdk
- Patch1: do not source rpm backup files or temporary files from /etc/wlan/shared,
  thus avoiding an endless loop (#5773)

* Tue Feb 08 2005 Olivier Blin <oblin@mandrakesoft.com> 0.2.1-0.pre26.1mdk
- 0.2.1pre26

* Thu Nov 18 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 0.2.1-0.pre23.1mdk
- 0.2.1pre23
- be sure to usr kernel source from /usr/src/linux
- update url
- don't wipe out buildroot in %%pre

* Wed Sep 29 2004 Olivier Blin <blino@mandrake.org> 0.2.1-0.pre21.2mdk
- Patch0: do not use prism2_cs for "I-GATE 11M PC Card / PC Card Plus"
  (bug 11248, thanks to Leo Milano)

* Wed Aug 11 2004 Laurent Culioli <laurent@mandrake.org> 0.2.1-0.pre21.1mdk
- 0.2.1pre21

