%define module fcdsl2
%define version 3.11.07
%define card "AVM Audiovisuelles|Fritz DSL Ver. 2.0"

Summary: dkms package for %{module} driver
Name: dkms-%{module}
Version: %{version}
Release: %mkrel 6
Source0: ftp://ftp.avm.de/cardware/fritzcrd.dsl_v20/linux/suse.93/fcdsl2-suse93-3.11-07.tar.bz2
Patch0: fritz-xchg.patch
License: Commercial
Group: System/Kernel and hardware
URL: http://www.avm.de/
Requires(post): dkms
Requires(preun): dkms
BuildRoot: %{_tmppath}/%{name}-buildroot
BuildArch: noarch

%description
This package contains the %{module} driver for %{card}

%prep
%setup -n fritz/src -q
%patch0 -p2 -b .xchg
# copy the lib in the source tree, do not use some obscure place like /var/lib/fritz
cp ../lib/*.o .
# do not try to copy the lib in LIBDIR
perl -pi -e 's!.*cp -f \.\./lib.*!!' Makefile
# fool Makefile by using a already existing LIBDIR
perl -pi -e 's!(LIBDIR.*):=.*!$1:= \$(SUBDIRS)!' Makefile
#- dkms pass KERNELRELEASE and confuse the Makefile, rely on KERNELVERSION instead
perl -pi -e 's!(ifneq.*)KERNELRELEASE!$1KERNELVERSION!' Makefile
#- build for kernel release dkms is asking for
perl -pi -e 's!shell uname -r!KERNELRELEASE!' Makefile

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/src/%module-%version/
cat > $RPM_BUILD_ROOT/usr/src/%module-%version/dkms.conf <<EOF
PACKAGE_NAME=%module
PACKAGE_VERSION=%version

DEST_MODULE_LOCATION[0]=/kernel/drivers/isdn/capi
BUILT_MODULE_NAME[0]=%module
MAKE[0]="make"
CLEAN="make clean"
AUTOINSTALL="yes"
EOF

tar c . | tar x -C $RPM_BUILD_ROOT/usr/src/%module-%version/

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%attr(0755,root,root) /usr/src/%module-%version/

%post
set -x
/usr/sbin/dkms --rpm_safe_upgrade add -m %module -v %version 
/usr/sbin/dkms --rpm_safe_upgrade build -m %module -v %version
/usr/sbin/dkms --rpm_safe_upgrade install -m %module -v %version

%preun
set -x
/usr/sbin/dkms --rpm_safe_upgrade remove -m %module -v %version --all


