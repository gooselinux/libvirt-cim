# -*- rpm-spec -*-

Summary: A CIM provider for libvirt
Name: libvirt-cim
Version: 0.5.8
Release: 3%{?dist}
License: LGPLv2+
Group: Development/Libraries
Source: libvirt-cim-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
URL: http://libvirt.org/CIM/
Requires: unzip
Requires: tog-pegasus 
BuildRequires: libcmpiutil >= 0.4
BuildRequires: tog-pegasus-devel
BuildRequires: libvirt-devel >= 0.6.3
BuildRequires: e2fsprogs-devel
BuildRequires: libxml2-devel >= 2.6.0
BuildRequires: libuuid-devel
BuildRequires: libcmpiutil-devel
BuildConflicts: sblim-cmpi-devel

# list of patches from mercurial since 0.5.8 was released
Patch0: libvirt-cim-0.5.8-xen-net-source.patch
Patch1: libvirt-cim-0.5.8-bug-dup.patch
Patch2: libvirt-cim-0.5.8-floppy.patch
Patch3: libvirt-cim-0.5.8-storage-volume-byte.patch
Patch4: libvirt-cim-0.5.8-net-device-change.patch
Patch5: libvirt-cim-0.5.8-vepa.patch
Patch6: libvirt-cim-0.5.8-storage-volume-path.patch

%description
Libvirt-cim is a CMPI CIM provider that implements the DMTF SVPC
virtualization model. The goal is to support most of the features
exported by libvirt itself, enabling management of multiple
platforms with a single provider.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1

chmod -f -x src/* libxkutil/* schema/* README doc/* #base_schema/README*
chmod +X src/* libxkutil/* schema/*

%build
%configure --disable-werror
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}

%install
rm -fr $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install
rm -f $RPM_BUILD_ROOT%{_libdir}/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/cmpi/*.la
rm -f $RPM_BUILD_ROOT%{_libdir}/cmpi/*.a
rm -f $RPM_BUILD_ROOT%{_libdir}/libxkutil.so
mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d
echo %{_libdir}/cmpi > $RPM_BUILD_ROOT/etc/ld.so.conf.d/libvirt-cim.%{_arch}.conf
mkdir -p $RPM_BUILD_ROOT/etc/libvirt/cim

%clean
rm -fr $RPM_BUILD_ROOT

%pre
%define REGISTRATION %{_datadir}/%{name}/*.registration
%define SCHEMA %{_datadir}/%{name}/*.mof

%define INTEROP_REG %{_datadir}/%{name}/{RegisteredProfile,ElementConformsToProfile,ReferencedProfile}.registration
%define INTEROP_MOF %{_datadir}/%{name}/{ComputerSystem,HostSystem,RegisteredProfile,DiskPool,MemoryPool,NetPool,ProcessorPool,VSMigrationService,ElementConformsToProfile,ReferencedProfile,AllocationCapabilities}.mof

%define PGINTEROP_REG %{_datadir}/%{name}/{RegisteredProfile,ElementConformsToProfile,ReferencedProfile}.registration
%define PGINTEROP_MOF %{_datadir}/%{name}/{RegisteredProfile,ElementConformsToProfile,ReferencedProfile}.mof

%define CIMV2_REG %{_datadir}/%{name}/{HostedResourcePool,ElementCapabilities,HostedService,HostedDependency,ElementConformsToProfile,HostedAccessPoint}.registration
%define CIMV2_MOF %{_datadir}/%{name}/{HostedResourcePool,ElementCapabilities,HostedService,HostedDependency,RegisteredProfile,ComputerSystem,ElementConformsToProfile,HostedAccessPoint}.mof

# _If_ there is already a version of this installed, we must deregister
# the classes we plan to install in post, otherwise we may corrupt
# the pegasus repository.  This is convention in other provider packages

%{_datadir}/%{name}/provider-register.sh -d -t pegasus \
	-n root/virt \
	-r %{REGISTRATION} -m %{SCHEMA} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -d -t pegasus \
        -n root/interop \
        -r %{INTEROP_REG} -m %{INTEROP_MOF} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -d -t pegasus \
        -n root/PG_InterOp \
        -r %{PGINTEROP_REG} -m %{PGINTEROP_MOF} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -d -t pegasus \
        -n root/cimv2\
        -r %{CIMV2_REG} -m %{CIMV2_MOF} >/dev/null 2>&1 || true

%post
/sbin/ldconfig

%{_datadir}/%{name}/install_base_schema.sh %{_datadir}/%{name}

/etc/init.d/tog-pegasus condrestart

# Register MOFs
# NOTE: root/virt is registered twice, this is needed to actually
#       get a proper registration

%{_datadir}/%{name}/provider-register.sh -t pegasus \
	-n root/virt \
	-r %{REGISTRATION} -m %{SCHEMA} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -t pegasus \
	-n root/virt \
	-r %{REGISTRATION} -m %{SCHEMA} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -t pegasus \
        -n root/interop \
        -r %{INTEROP_REG} -m %{INTEROP_MOF} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -t pegasus \
        -n root/PG_InterOp \
        -r %{PGINTEROP_REG} -m %{PGINTEROP_MOF} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -t pegasus \
        -n root/cimv2\
        -r %{CIMV2_REG} -m %{CIMV2_MOF} >/dev/null 2>&1 || true

%preun

# Unregister MOFs

%{_datadir}/%{name}/provider-register.sh -d -t pegasus \
	-n root/virt \
	-r %{REGISTRATION} -m %{SCHEMA} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -d -t pegasus \
        -n root/interop \
        -r %{INTEROP_REG} -m %{INTEROP_MOF} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -d -t pegasus \
        -n root/PG_InterOp \
        -r %{PGINTEROP_REG} -m %{PGINTEROP_MOF} >/dev/null 2>&1 || true
%{_datadir}/%{name}/provider-register.sh -d -t pegasus \
        -n root/cimv2\
        -r %{CIMV2_REG} -m %{CIMV2_MOF} >/dev/null 2>&1 || true

%postun -p /sbin/ldconfig

%files
%defattr(-, root, root)
%{_sysconfdir}/libvirt/cim

%doc README COPYING doc/CodingStyle doc/SubmittingPatches
%doc base_schema/README.DMTF
%doc doc/*.html
%{_libdir}/lib*.so*
# CIM providers are .so modules, thus they belong in the main package
%{_libdir}/cmpi/lib*.so*
%{_datadir}/libvirt-cim
%{_datadir}/libvirt-cim/*.sh
%{_datadir}/libvirt-cim/*.mof
%{_datadir}/libvirt-cim/cimv*-interop_mof
%{_datadir}/libvirt-cim/cimv*-cimv2_mof
%{_datadir}/libvirt-cim/*.registration
%{_datadir}/libvirt-cim/cim_schema_*-MOFs.zip
%{_sysconfdir}/ld.so.conf.d/libvirt-cim.%{_arch}.conf

%changelog
* Fri May 14 2010 Daniel Veillard <veillard@redhat.com> - 0.5.8-3.el6
- fix a multi arch problem
- Resolves: rhbz#587232

* Fri Apr  9 2010 Daniel Veillard <veillard@redhat.com> - 0.5.8-2.el6
- add a set of patches coming from upstream after 0.5.8
- Resolves: rhbz#569570

* Wed Jan 20 2010 Daniel Veillard <veillard@redhat.com> - 0.5.8-1.el6
- update to new version 0.5.8
- Resolves: rhbz#557300

* Tue Oct 5 2009 Kaitlin Rupert <kaitlin@us.ibm.com> - 0.5.7-1
- Updated to latest upstream source

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.6-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 14 2009 Kaitlin Rupert <kaitlin@us.ibm.com> - 0.5.6-1
- Updated to latest upstream source

* Tue Apr 21 2009 Kaitlin Rupert <kaitlin@us.ibm.com> - 0.5.5-1
- Updated to latest upstream source

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 17 2009 Kaitlin Rupert <kaitlin@us.ibm.com> - 0.5.4-1
- Updated to latest upstream source

* Thu Jan 15 2009 Kaitlin Rupert <kaitlin@us.ibm.com> - 0.5.3-1
- Updated to latest upstream source

* Mon Oct 06 2008 Kaitlin Rupert <kaitlin@us.ibm.com> - 0.5.2-1
- Updated to latest upstream source

* Tue Sep 23 2008 Kaitlin Rupert <kaitlin@us.ibm.com> - 0.5.1-5
- Added vsmigser_schema patch to remove dup method name from VSMigrationService
- Added mem_parse patch to set proper mem max_size and mem values
- Added mig_prof_ver patch to report the proper Migration Profile version
- Added hyp_conn_fail patch to fix when not connecting to hyp returns a failure
- Added rm_def_virtdev patch to remove default DiskRADSD virtual device
- Added rm_eafp_err patch to remove error status when EAFP no pool link exists
- Added sdc_unsup patch to make SDC not return unsup for RASD to AC case

* Wed Aug 27 2008 Kaitlin Rupert <kaitlin@us.ibm.com> - 0.5.1-4
- Added nostate patch to consider XenFV no state guests as running guests
- Added createsnap_override patch to add vendor defined values to CreateSnapshot
- Added add_shutdown_rsc patch to add support for shutdown operation
- Added vsmc_add_remove patch to expose Add/Remove resources via VSMC
- Added override_refconf patch to fix dup devs where ID matches refconf dev ID

* Thu Aug 07 2008 Dan Smith <danms@us.ibm.com> - 0.5.1-3
- Added infostore_trunc patch to fix infostore corruption
- Added vsss_paramname patch to fix VSSS parameter name
- Added vsss_logic patch to fix terminal memory snapshot logic
- Added /etc/libvirt/cim directory for infostore

* Thu Jul 31 2008 Dan Smith <danms@us.ibm.com> - 0.5.1-1
- Updated to latest upstream source

* Thu Jun 03 2008 Dan Smith <danms@us.ibm.com> - 0.5-1
- Updated to latest upstream source

* Fri May 30 2008 Dan Smith <danms@us.ibm.com> - 0.4-2
- Fixed schema registration to pick up ECTP in root/virt properly
- Fixed schema registration to include ReferencedProfile in interop
- Added RASD namespace fix

* Wed May 21 2008 Dan Smith <danms@us.ibm.com> - 0.4-1
- Updated to latest upstream source
- Added default disk pool configuration patch

* Fri Mar 14 2008 Dan Smith <danms@us.ibm.com> - 0.3-4
- Fixed loader config for 64-bit systems
- Added missing root/interop schema install
- Added RegisteredProfile.registration to install

* Fri Mar 07 2008 Dan Smith <danms@us.ibm.com> - 0.3-2
- Added KVM method enablement patch

* Mon Mar 03 2008 Dan Smith <danms@us.ibm.com> - 0.3-1
- Updated to latest upstream source

* Wed Feb 13 2008 Dan Smith <danms@us.ibm.com> - 0.2-1
- Updated to latest upstream source

* Thu Jan 17 2008 Dan Smith <danms@us.ibm.com> - 0.1-8
- Add ld.so.conf.d configuration

* Mon Jan 14 2008 Dan Smith <danms@us.ibm.com> - 0.1-7
- Update to offical upstream release
- Patch source to fix parallel make issue until fixed upstream

* Mon Jan 07 2008 Dan Smith <danms@us.ibm.com> - 0.1-3
- Remove RPATH on provider modules

* Mon Jan 07 2008 Dan Smith <danms@us.ibm.com> - 0.1-2
- Cleaned up Release
- Removed unnecessary Requires
- After install, condrestart pegasus
- Updated to latest source snapshot

* Fri Oct 26 2007 Daniel Veillard <veillard@redhat.com> - 0.1-1
- created
