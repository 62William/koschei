%bcond_without tests

Name:           koschei
Version:        0.1
Release:        2%{?dist}
Summary:        Continuous integration for Fedora packages
License:        GPLv2+
URL:            https://github.com/msimacek/%{name}
Source0:        https://github.com/msimacek/%{name}/archive/%{name}-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python2-devel
BuildRequires:  python-setuptools
BuildRequires:  systemd

%if %{with tests}
BuildRequires:       python-nose
BuildRequires:       python-mock
BuildRequires:       python-sqlalchemy
BuildRequires:       koji
BuildRequires:       python-hawkey
BuildRequires:       python-librepo
BuildRequires:       python-libcomps
BuildRequires:       rpm-python
%endif

Requires:       python-sqlalchemy
Requires:       koji
Requires:       fedmsg
Requires:       postgresql-server
Requires:       python-psycopg2
Requires:       createrepo_c
Requires:       curl
Requires:       python-jinja2
Requires:       python-hawkey
Requires:       python-alembic
Requires:       python-flask
Requires:       python-flask-sqlalchemy
Requires:       mod_wsgi
Requires:       httpd
Requires:       python-librepo
Requires:       python-libcomps
Requires:       rpm-python
Requires(pre):  shadow-utils
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
Service tracking dependency changes in Fedora and rebuilding packages whose
dependencies change too much. It uses Koji scratch builds to do the rebuilds and
provides a web interface to the results.

%prep
%setup -q -n %{name}-%{name}-%{version}

sed 's|@CACHEDIR@|%{_localstatedir}/cache/%{name}|g
     s|@DATADIR@|%{_datadir}/%{name}|g' config.cfg.template > config.cfg

%build
%{__python2} setup.py build

%install
%{__python2} setup.py install --skip-build --root %{buildroot}

mkdir -p %{buildroot}%{_sysconfdir}/%{name}
cp -p config.cfg %{buildroot}%{_sysconfdir}/%{name}/

install -dm 755 %{buildroot}%{_unitdir}
for unit in systemd/*; do
    install -pm 644 $unit %{buildroot}%{_unitdir}/
done

mkdir -p %{buildroot}%{_bindir}
install -pm 755 admin.py %{buildroot}%{_bindir}/%{name}-admin

install -dm 755 %{buildroot}%{_localstatedir}/cache/%{name}/repodata
install -dm 755 %{buildroot}%{_localstatedir}/cache/%{name}/srpms

mkdir -p %{buildroot}%{_datadir}/%{name}
cp -pr templates %{buildroot}%{_datadir}/%{name}/

cp -pr alembic/ alembic.ini %{buildroot}%{_datadir}/%{name}/
cp -pr theme %{buildroot}%{_datadir}/%{name}/
ln -s theme/fedora/static %{buildroot}%{_datadir}/%{name}/static
cp -p %{name}.wsgi %{buildroot}%{_datadir}/%{name}/
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
cp -p httpd.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

%if %{with tests}
%check
%{__python2} setup.py test
%endif

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
# services and koschei-admin script is supposed to be run as this user
getent passwd %{name} >/dev/null || \
    useradd -r -g %{name} -d %{_datadir}/%{name} -s /bin/sh \
    -c "Runs %{name} services" %{name}
exit 0

%post
%systemd_post %{name}-scheduler.service
%systemd_post %{name}-watcher.service
%systemd_post %{name}-polling.service
%systemd_post %{name}-resolver.service

%preun
%systemd_preun %{name}-scheduler.service
%systemd_preun %{name}-watcher.service
%systemd_preun %{name}-polling.service
%systemd_preun %{name}-resolver.service

%postun
%systemd_postun_with_restart %{name}-scheduler.service
%systemd_postun_with_restart %{name}-watcher.service
%systemd_postun_with_restart %{name}-polling.service
%systemd_postun_with_restart %{name}-resolver.service

%files
%doc LICENSE.txt
%{_bindir}/%{name}-admin
%{_datadir}/%{name}
%attr(755, %{name}, %{name}) %{_localstatedir}/cache/%{name}
%{python2_sitelib}/*
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/config.cfg
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%{_unitdir}/*

%changelog
* Mon Sep 01 2014 Michael Simacek <msimacek@redhat.com> - 0.1-2
- Fixed BR python-devel -> python2-devel
- Fixed changelog format
- Added noreplace to httpd config
- Replaced name occurences with macro

* Fri Jun 13 2014 Michael Simacek <msimacek@redhat.com> - 0.1-1
- Initial version
