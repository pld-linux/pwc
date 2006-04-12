#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace package
%bcond_with	verbose		# verbose build (V=1)
#
%define	_module_file_name	pwc-unofficial
#
%define		_rel	1
Summary:	PWC - module with decompressor for Philips USB webcams
Summary(pl):	PWC - modu³ z dekompresorem obrazu dla kamer internetowych Philipsa
Name:		pwc
Version:	10.0.10
Release:	%{_rel}
License:	GPL
Group:		Applications/Multimedia
Source0:	http://www.saillard.org/linux/pwc/files/%{name}-%{version}.tar.bz2
# Source0-md5:	a29423adf03d07bee824fe1627911b94
Patch0:		%{name}-hotfix-for-kernel-2.6.10.patch
URL:		http://www.saillard.org/linux/pwc/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Module with decompressor for Philips webcams, this allows you to use
higher resolution and framerate. Working cameras:
- Philips: PCA645VC and 646VC, "Vesta", "Vesta Pro", "Vesta Scan",
  "ToUCam XS" (PCVC720K/40,/20 is supported by ov511), "ToUCam Fun",
  "ToUCam Pro", "ToUCam Scan", "ToUCam II", "ToUCam Pro II"
- Askey VC010
- Creative Labs Webcam: 5 (the old one; USB Product ID: 0x400C)
- Pro Ex Logitech QuickCam 3000 Pro, 4000 Pro, Notebook Pro, Zoom and
  Orbit/Sphere
- Samsung MPC-C10 and MPC-C30
- Sotec Afina Eye
- Visionite VCS UM100 and VCS UC300

%description -l pl
Modu³ z dekompresorem obrazu dla kamer na uk³adzie Philipsa. Pozwala
na uzyskanie wiêkszej rozdzielczo¶ci i ilo¶ci klatek. Obs³ugiwane
kamery:
- Philips: PCA645VC and 646VC, "Vesta", "Vesta Pro", "Vesta Scan",
  "ToUCam XS" (PCVC720K/40, K/20 dzia³a z ov511), "ToUCam Fun", "ToUCam
  Pro", "ToUCam Scan", "ToUCam II", "ToUCam Pro II"
- Askey VC010
- Creative Labs Webcam: 5 (stary typ; USB Product ID: 0x400C)
- Pro Ex Logitech QuickCam 3000 Pro, 4000 Pro, Notebook Pro, Zoom i
  Orbit/Sphere
- Samsung MPC-C10 and MPC-C30
- Sotec Afina Eye
- Visionite VCS UM100 i VCS UC300.

%package -n kernel-video-pwc
Summary:	Linux driver for Philips USB webcams
Summary(pl):	Sterownik dla Linuksa do kamer internetowych Philipsa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
%endif

%description -n kernel-video-pwc
This is driver for Philips USB webcams for Linux.

This package contains Linux module. File is called
%{_module_file_name}.

%description -n kernel-video-pwc -l pl
Sterownik dla Linuksa do kamer internetowych Philipsa.

Ten pakiet zawiera modu³ j±dra Linuksa. Plik nazywa siê
%{_module_file_name}.

%package -n kernel-smp-video-pwc
Summary:	Linux SMP driver for Philips USB webcams
Summary(pl):	Sterownik dla Linuksa SMP do kamer internetowych Philipsa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
%endif

%description -n kernel-smp-video-pwc
This is driver for Philips USB webcams for Linux.

This package contains Linux SMP module. File is called
%{_module_file_name}.

%description -n kernel-smp-video-pwc -l pl
Sterownik dla Linuksa do kamer internetowych Philipsa.

Ten pakiet zawiera modu³ j±dra Linuksa SMP. Plik nazywa siê
%{_module_file_name}.

%prep
%setup -q
%patch0 -p0
grep -E "^pwc-objs" Makefile > Makefile.new
echo "obj-m	+= pwc.o" >> Makefile.new
echo "CFLAGS	+= -DXAWTV_HAS_BEEN_FIXED=1" >> Makefile.new
mv -f Makefile{.new,}
cp -f pwc-if.c pwc-if.c.orig

%build
%if %{with kernel}
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
	if grep -q "^CONFIG_PREEMPT_RT=y$" o/.config; then
		sed 's/SPIN_LOCK_UNLOCKED/SPIN_LOCK_UNLOCKED(pdev->ptrlock)/' \
			pwc-if.c.orig > pwc-if.c
	else
		cat pwc-if.c.orig > pwc-if.c
	fi

	%if %{with dist_kernel}
		%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
	%else
		install -d o/include/config
		touch o/include/config/MARKER
		ln -sf %{_kernelsrcdir}/scripts o/scripts
	%endif
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	mv pwc{,-$cfg}.ko
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}{,smp}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/usb/media
install pwc-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb/media/%{_module_file_name}.ko
echo "alias pwc %{_module_file_name}" \
	> $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}/pwc.conf
%if %{with smp} && %{with dist_kernel}
install pwc-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/media/%{_module_file_name}.ko
echo "alias pwc %{_module_file_name}" \
	> $RPM_BUILD_ROOT%{_sysconfdir}/modprobe.d/%{_kernel_ver}smp/pwc.conf
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-video-pwc
%depmod %{_kernel_ver}

%postun -n kernel-video-pwc
%depmod %{_kernel_ver}

%post -n kernel-smp-video-pwc
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-video-pwc
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files -n kernel-video-pwc
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/media/%{_module_file_name}*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}/pwc.conf

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-video-pwc
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/media/%{_module_file_name}*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}smp/pwc.conf
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%endif
