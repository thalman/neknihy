#
# build command: rpmbuild -ba neknihy.spec -D "SRCVERSION x.y.z"
#
Name:           neknihy
Version:        %{SRCVERSION}
Release:        1%{?dist}
Summary:        Desktop client for Palmknihy web rental service.
License:        GPLv3
URL:            https://github.com/thalman/neknihy
Source0:        https://github.com/thalman/neknihy/releases/download/v%{version}/neknihy-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3-devel
Requires:       python3-gobject
Requires:       python3-tkinter

%description
Simple desktop client to PalmKnihy web rental system.

%prep
%setup -q

%build
true

%clean
/bin/rm -rf ${RPM_BUILD_ROOT}

%install
install -d ${RPM_BUILD_ROOT}%{_datadir}/applications
install -d ${RPM_BUILD_ROOT}%{_libexecdir}/neknihy/{neknihy,resources}

install -m 755 src/neknihy.py ${RPM_BUILD_ROOT}%{_libexecdir}/neknihy/
install -m 644 src/neknihy/*.py ${RPM_BUILD_ROOT}%{_libexecdir}/neknihy/neknihy/
install src/resources/*.png ${RPM_BUILD_ROOT}%{_libexecdir}/neknihy/resources/

sed 's#@LIBEXECDIR@#%{_libexecdir}#' < contrib/neknihy.desktop > ${RPM_BUILD_ROOT}%{_datadir}/applications/neknihy.desktop

%files
%doc README.md
%license LICENSE
%{_libexecdir}/neknihy
%{_datadir}/applications/neknihy.desktop

%changelog
* Tue Oct 24 2023 Tomas Halman <tomas@halman.net>
  neknihy relased

