#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	up		# don't build UP module
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace package
%bcond_with	verbose		# verbose build (V=1)
#
%define	_module_suffix	unofficial
#
%define		_rc	rc1
%define		_rel	0.%{_rc}.1
Summary:	PWC - module with decompressor for Philips USB webcams
Summary(pl.UTF-8):	PWC - moduł z dekompresorem obrazu dla kamer internetowych Philipsa
Name:		pwc
Version:	10.0.12
Release:	%{_rel}
License:	GPL
Group:		Applications/Multimedia
Source0:	http://www.saillard.org/linux/pwc/files/%{name}-%{version}-%{_rc}.tar.bz2
# Source0-md5:	8763f3d6fd0f9738ef9854de205a126d
Patch0:		%{name}-hotfix-for-kernel-2.6.10.patch
URL:		http://www.saillard.org/linux/pwc/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.330
BuildRequires:	sed >= 4.0
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

%description -l pl.UTF-8
Moduł z dekompresorem obrazu dla kamer na układzie Philipsa. Pozwala
na uzyskanie większej rozdzielczości i ilości klatek. Obsługiwane
kamery:
- Philips: PCA645VC and 646VC, "Vesta", "Vesta Pro", "Vesta Scan",
  "ToUCam XS" (PCVC720K/40, K/20 działa z ov511), "ToUCam Fun", "ToUCam
  Pro", "ToUCam Scan", "ToUCam II", "ToUCam Pro II"
- Askey VC010
- Creative Labs Webcam: 5 (stary typ; USB Product ID: 0x400C)
- Pro Ex Logitech QuickCam 3000 Pro, 4000 Pro, Notebook Pro, Zoom i
  Orbit/Sphere
- Samsung MPC-C10 and MPC-C30
- Sotec Afina Eye
- Visionite VCS UM100 i VCS UC300.

%package -n kernel%{_alt_kernel}-video-pwc
Summary:	Linux driver for Philips USB webcams
Summary(pl.UTF-8):	Sterownik dla Linuksa do kamer internetowych Philipsa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
%endif

%description -n kernel%{_alt_kernel}-video-pwc
This is driver for Philips USB webcams for Linux.

This package contains Linux module. File is called
%{_module_file_name}.

%description -n kernel%{_alt_kernel}-video-pwc -l pl.UTF-8
Sterownik dla Linuksa do kamer internetowych Philipsa.

Ten pakiet zawiera moduł jądra Linuksa. Plik nazywa się
%{_module_file_name}.

%package -n kernel%{_alt_kernel}-smp-video-pwc
Summary:	Linux SMP driver for Philips USB webcams
Summary(pl.UTF-8):	Sterownik dla Linuksa SMP do kamer internetowych Philipsa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
%endif

%description -n kernel%{_alt_kernel}-smp-video-pwc
This is driver for Philips USB webcams for Linux.

This package contains Linux SMP module. File is called
%{_module_file_name}.

%description -n kernel%{_alt_kernel}-smp-video-pwc -l pl.UTF-8
Sterownik dla Linuksa do kamer internetowych Philipsa.

Ten pakiet zawiera moduł jądra Linuksa SMP. Plik nazywa się
%{_module_file_name}.

%prep
%setup -q -n %{name}-%{version}-%{_rc}
%patch -P0 -p0
grep -E "^pwc-objs" Makefile > Makefile.new
echo "obj-m	+= pwc.o" >> Makefile.new
echo "CFLAGS	+= -DXAWTV_HAS_BEEN_FIXED=1" >> Makefile.new
mv -f Makefile{.new,}
cp -f pwc-if.c pwc-if.c.orig
sed -e '/#include <linux.videodev2.h>/a#include <media/v4l2-dev.h>' -i pwc.h

%build
%if %{with kernel}
%build_kernel_modules T=$TMPDIR -m pwc <<'EOF'
# patch only if kernel compiled with realtime-preempt patch
if grep -q "CONFIG_PREEMPT_RT" o/.config; then
	sed 's/SPIN_LOCK_UNLOCKED/SPIN_LOCK_UNLOCKED(pdev->ptrlock)/' \
		pwc-if.c.orig > pwc-if.c
else
	cat pwc-if.c.orig > pwc-if.c
fi
EOF
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
%install_kernel_modules -s %{_module_suffix} -n %{name} -m pwc -d kernel/drivers/usb/media
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-video-pwc
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-video-pwc
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-video-pwc
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-video-pwc
%depmod %{_kernel_ver}smp

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-video-pwc
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/media/pwc-%{_module_suffix}.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}/%{name}.conf
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-video-pwc
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/media/pwc-%{_module_suffix}.ko*
%{_sysconfdir}/modprobe.d/%{_kernel_ver}smp/%{name}.conf
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%endif
