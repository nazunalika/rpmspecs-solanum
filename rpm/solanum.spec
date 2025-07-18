# Define global settings
%global _hardened_build 1
%global major_version 0
%global minor_version 0
%global micro_version 1
%global commit       70d491d8a4ad9fa02ce5394d9007baf5f23ca61c
%global commit_short 70d491d8
%global date         20250708
%global relnum       16

# Need to figure out what's going on with this. This is temporary for f35
%global __brp_check_rpaths %{nil}

Name:		solanum
Version:	%{major_version}.%{minor_version}.%{micro_version}
Release:	%{relnum}.%{date}.%{commit_short}%{?dist}
Summary:	A highly-scalable IRCv3-compliant IRC daemon

Group:		Applications/Communications
License:	GPLv2
URL:		https://solanum.chat/
#Source0:	https://github.com/%{name}-ircd/%{name}/archive/%{name}-%{version}.tar.gz
Source1:	%{name}.service
Source2:	%{name}.tmpfiles
Source3:	%{name}.conf
#Source4:	%{name}.README

Provides:	%{name} = %{version}-%{release}

BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	gcc
BuildRequires:	gcc-c++
BuildRequires:	libtool
BuildRequires:	libtool-ltdl-devel
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(libcrypto)
BuildRequires:	git

BuildRequires:		systemd
Requires(post):		systemd
Requires(preun):	systemd
Requires(postun):	systemd
Requires(pre):		shadow-utils

Requires:	openssl

%description
Solanum is an IRCv3 server designed to be highly scalable. It implements IRCv3.1
and some parts of IRCv3.2.

It is meant to be used with an IRCv3-capable services implementation such as
Atheme or Anope.

Solanum is an ircd used on various networks either as itself, or as the basis of
a customized IRC server implementation.

%prep
#%setup -q -n %{name}-%{version}
# No release tars
rm -rf %{name}-%{commit} %{name} %{name}-%{version}
git clone https://github.com/solanum-ircd/solanum.git %{name}-%{version}
# No release tars

%build
# No release tars
%if 0%{?rhel} <= 9
cd %{name}-%{version}
%endif
git checkout %{commit}
# No release tars

/bin/sh ./autogen.sh
%configure --prefix=%{_prefix} \
	--with-program-prefix=solanum- \
	--enable-fhs-paths \
	--with-rundir=/run \
	--sysconfdir=%{_sysconfdir}/%{name} \
	--with-moduledir=%{_libdir}/%{name} \
	--with-logdir=%{_var}/log/%{name} \
	--localstatedir=%{_sharedstatedir} \
	--libexecdir=%{_libexecdir} \
	--enable-openssl \
	--enable-ipv6 \
	--enable-epoll \
	--with-shared-sqlite

make %{?_smp_mflags} SOLANUM_VERSION="%{version}"

# Extra readme
#cp %{SOURCE4} %{_builddir}/%{name}/README.info

%install
rm -rf $RPM_BUILD_ROOT

# No release tars
cd %{name}-%{version}
# No release tars

%make_install

# Move the binaries to the libexec directory, since it's
# more appropriate. This could change in the future.
%{__install} -d -m 0755 ${RPM_BUILD_ROOT}/%{_libexecdir}/%{name}
%{__mv} ${RPM_BUILD_ROOT}/%{_bindir}/* \
	${RPM_BUILD_ROOT}/%{_libexecdir}/%{name}

# Install service
%{__install} -d -m 0755 ${RPM_BUILD_ROOT}%{_unitdir}
%{__install} -m 0644 %{SOURCE1} \
        ${RPM_BUILD_ROOT}%{_unitdir}/%{name}.service

# Install tmpfiles
%{__install} -d -m 0755 ${RPM_BUILD_ROOT}%{_tmpfilesdir}
%{__install} -m 0644 %{SOURCE2} \
	${RPM_BUILD_ROOT}%{_tmpfilesdir}/%{name}.conf

# Install ircd.conf
%{__install} -m 0660 %{SOURCE3} \
	${RPM_BUILD_ROOT}%{_sysconfdir}/%{name}/ircd.conf

# Create log and shared state
%{__install} -d -m 0750 ${RPM_BUILD_ROOT}%{_sharedstatedir}/%{name}
%{__install} -d -m 0750 ${RPM_BUILD_ROOT}%{_var}/log/%{name}

# Removing development libraries
rm -rf ${RPM_BUILD_ROOT}%{_libdir}/pkgconfig
rm -f  ${RPM_BUILD_ROOT}%{_libdir}/*.la

%pre
%{_sbindir}/groupadd -r %{name} 2>/dev/null || :
%{_sbindir}/useradd -r -g %{name} \
	-s /sbin/nologin -d %{_datadir}/%{name} \
	-c 'Solanum Server' %{name} 2>/dev/null || :

%preun
%if 0%{?fedora} || 0%{?rhel} >= 7
%systemd_preun %{name}.service
%endif

%post
%if 0%{?fedora} || 0%{?rhel} >= 7
%systemd_post %{name}.service
systemd-tmpfiles --create %{name}.conf || :
%endif

%postun
%if 0%{?fedora} || 0%{?rhel} >= 7
%systemd_postun_with_restart %{name}.service
%endif


%files
%defattr(-, root, root, -)
#%doc doc/logfiles.txt doc/credits-past.txt doc/features/* doc/oper-guide/* doc/technical/* doc/modes.txt doc/server-version-info.txt CREDITS LICENSE NEWS.md README.md
%dir %attr(0750,solanum,solanum) %{_var}/log/%{name}
%dir %attr(0750,solanum,solanum) %{_sharedstatedir}/%{name}
%dir %attr(0750,root,solanum) %{_sysconfdir}/%{name}
%dir %{_libexecdir}/%{name}
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/autoload
%dir %{_libdir}/%{name}/extensions
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/help
%dir %{_datadir}/%{name}/help/opers
%dir %{_datadir}/%{name}/help/users
%{_libdir}/*.so
%{_libdir}/%{name}/*.so
%{_libdir}/%{name}/autoload/*.so
%{_libdir}/%{name}/extensions/*.so
%{_datadir}/%{name}/help/opers/*
%{_datadir}/%{name}/help/users/*
%{_unitdir}/%{name}.service

%attr(0755,solanum,solanum) %{_libexecdir}/%{name}/*

# Default configuration
%config(noreplace) %attr(0640,solanum,solanum) %{_sysconfdir}/%{name}/ircd.conf
%config(noreplace) %attr(0640,solanum,solanum) %{_sysconfdir}/%{name}/ircd.motd

%attr(0640,solanum,solanum) %{_sysconfdir}/%{name}/*.example
%config(noreplace) %attr(0640,solanum,solanum) %{_sysconfdir}/%{name}/reference.conf

#%{_mandir}/man8/solanum-ircd.8*
%{_tmpfilesdir}/%{name}.conf

# Excludes - commented since we're using rm instead at build
#%exclude %{_libdir}/*.la
#%exclude %dir %{_libdir}/pkgconfig
#%exclude %{_libdir}/pkgconfig/libratbox.pc

%changelog
* Tue Jul 08 2025 Louis Abel <tucklesepk@gmail.com> - 0.0.1-16.20250708.70d491d8
- Update to latest commit

* Thu Apr 10 2025 Louis Abel <tucklesepk@gmail.com> - 0.0.1-15.20250410.1669c640
- Update to latest commit

* Thu Mar 21 2024 Louis Abel <tucklesepk@gmail.com> - 0.0.1-14.20240321.dd335573
- Update to latest commit

* Sat Jan 27 2024 Louis Abel <tucklesepk@gmail.com> - 0.0.1-14.20240127.1ccc6422
- Update to latest commit

* Thu Nov 16 2023 Louis Abel <tucklesepk@gmail.com> - 0.0.1-13.20231116.4d12e654
- Update to latest commit

* Mon Jul 24 2023 Louis Abel <tucklesepk@gmail.com> - 0.0.1-12.20230724.0ca18d07
- Update to latest commit
- Clear changelog
