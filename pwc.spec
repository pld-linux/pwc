#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	PWC - decompressor modules for Philips USB webcams
Summary(pl):	PWC - modu³y dekompresuj±ce obraz z kamer internetowych Philipsa
Name:		pwc
Version:	10.0.7
%define		_rel	1
Release:	%{_rel}
License:	GPL
Group:		Applications/Multimedia
Source0:	http://www.saillard.org/linux/pwc/files/%{name}-%{version}.tar.bz2
# Source0-md5:	920ac4cb4feacb345b1dcfd19de28448
Patch0:		%{name}-Makefile.patch
Patch1:		%{name}-hotfix-for-kernel-2.6.10.patch
URL:		http://www.saillard.org/linux/pwc/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
BuildRequires:	pkgconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Decompresor module for Philips webcams, this allows you to use higher
resoluwion and framerate. Working cameras: Philips: PCA645VC and
646VC, "Vesta", "Vesta Pro", "Vesta Scan", "ToUCam XS" (PCVC720K/40,
/20 is supported by ov511), "ToUCam Fun", "ToUCam Pro", "ToUCam Scan",
"ToUCam II", "ToUCam Pro II"; Askey VC010; Creative Labs Webcam: 5
(the old one; USB Product ID: 0x400C) and Pro Ex Logitech QuickCam
3000 Pro, 4000 Pro, Notebook Pro, Zoom and Orbit/Sphere; Samsung
MPC-C10 and MPC-C30; Sotec Afina Eye; Visionite VCS UM100 and VCS
UC300.

%description -l pl
Modu³ dekompresuj±cy obraz z kamer na uk³adzie Philipsa. Pozwala na
uzyskanie wiêkszej rozdzielczo¶ci i ilo¶ci klatek. Obs³ugiwane kamery:
Philips: PCA645VC and 646VC, "Vesta", "Vesta Pro", "Vesta Scan",
"ToUCam XS" (PCVC720K/40, K/20 dzia³a z ov511), "ToUCam Fun", "ToUCam
Pro", "ToUCam Scan", "ToUCam II", "ToUCam Pro II"; Askey VC010;
Creative Labs Webcam: 5 (stary typ; USB Product ID: 0x400C) i Pro Ex
Logitech QuickCam 3000 Pro, 4000 Pro, Notebook Pro, Zoom i
Orbit/Sphere; Samsung MPC-C10 and MPC-C30; Sotec Afina Eye; Visionite
VCS UM100 i VCS UC300.

%package -n kernel-video-pwc
Summary:	Linux driver for Philips USB webcams
Summary(pl):	Sterownik dla Linuksa do kamer internetowych Philipsa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%requires_releq_kernel_up
%endif

%description -n kernel-video-pwc
This is driver for Philips USB webcams for Linux.

This package contains Linux module.

%description -n kernel-video-pwc -l pl
Sterownik dla Linuksa do kamer internetowych Philipsa.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-video-pwc
Summary:	Linux SMP driver for Philips USB webcams
Summary(pl):	Sterownik dla Linuksa SMP do kamer internetowych Philipsa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%requires_releq_kernel_smp
%endif

%description -n kernel-smp-video-pwc
This is driver for Philips USB webcams for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-video-pwc -l pl
Sterownik dla Linuksa do kamer internetowych Philipsa.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q
%patch0 -p1
%patch1 -p0

%build
%if %{with kernel}
# kernel module(s)
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	mv pwc{,-$cfg}.ko
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/usb/media
install pwc-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb/media/pwc.ko
%if %{with smp} && %{with dist_kernel}
install pwc-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/media/pwc.ko
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
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/media/pwc.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-video-pwc
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/media/pwc.ko*
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc philips.txt
%endif
