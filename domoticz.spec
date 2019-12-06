Summary:	Open source Home Automation System
Name:		domoticz
Version:	4.10717
Release:	3
License:	GPLv3+ and ASL 2.0 and Boost and BSD and MIT
Group:		Base
URL:		http://www.domoticz.com
Source0:	https://github.com/domoticz/domoticz/archive/%{version}.tar.gz
# Source0-md5:	1d5f5572ae43379a6d62023cb8da0e9b
Source1:	%{name}.service
Source2:	%{name}.conf
# Source says its version 4.9700, but it's really 4.10717
Patch1:		%{name}-version.patch
# Use system tinyxpath (https://github.com/domoticz/domoticz/pull/1759)
Patch2:		%{name}-tinyxpath.patch
# Use system openzwave includes
Patch3:		%{name}-openzwave.patch
# Work against Dev branch of OpenZWave upstream
Patch4:		%{name}-openzwave-Dev.patch
# Fix python detection (https://github.com/domoticz/domoticz/pull/1749)
Patch5:		%{name}-python.patch
Patch6:		domoticz-ozw-barrier-support-0002.patch
Patch7:		domoticz-cp-js.patch
BuildRequires:	boost-devel
BuildRequires:	cmake
BuildRequires:	curl-devel
BuildRequires:	libmosquitto-devel
BuildRequires:  libmosquittopp-devel
BuildRequires:	libopenzwave-devel >= 1.5.0
BuildRequires:	libstdc++-devel
BuildRequires:	libusb-devel
BuildRequires:	lua-devel
BuildRequires:	openssl-devel
BuildRequires:	python3-devel
BuildRequires:	sqlite-devel
BuildRequires:	systemd-devel
BuildRequires:	tinyxpath-devel
BuildRequires:	zlib-devel
Requires(pre):  /usr/sbin/groupadd
Requires(pre):  /usr/sbin/useradd
Requires(post):	systemd
Requires(postun):	systemd
Requires(preun):	systemd
Requires:       fonts-TTF-Google-Droid
Provides:	bundled(js-ace)
Provides:	bundled(js-angular-ui-bootstrap) = 0.13.4
Provides:	bundled(js-angularamd) = 0.2.1
Provides:	bundled(js-angularjs) = 1.5.8
Provides:	bundled(js-blockly)
Provides:	bundled(js-bootbox)
Provides:	bundled(js-bootstrap) = 3.2.0
Provides:	bundled(js-colpick)
Provides:	bundled(js-d3)
Provides:	bundled(js-datatables-datatools) = 2.2.3
Provides:	bundled(js-dateformat) = 1.2.3
Provides:	bundled(js-filesaver) = 0.0-git20140725
Provides:	bundled(js-highcharts) = 4.2.6
Provides:	bundled(js-html5shiv) = 3.6.2
Provides:	bundled(js-i18next) = 1.8.0
Provides:	bundled(js-ion-sound) = 3.0.6
Provides:	bundled(js-jquery) = 1.12.0
Provides:	bundled(js-jquery-noty) = 2.1.0
Provides:	bundled(js-less) = 1.3.0
Provides:	bundled(js-ngdraggable)
Provides:	bundled(js-nggrid)
Provides:	bundled(js-ozwcp)
Provides:	bundled(js-require) = 2.1.14
Provides:	bundled(js-respond) = 1.1.0
Provides:	bundled(js-wow) = 0.1.9
Provides:	bundled(js-zeroclipboard) = 1.0.4

%description
Domoticz is a Home Automation System that lets you monitor and
configure various devices like: Lights, Switches, various
sensors/meters like Temperature, Rain, Wind, UV, Electra, Gas, Water
and much more. Notifications/Alerts can be sent to any mobile device

%prep
%setup -q
%patch1 -p1 -b.version
%patch2 -p1 -b.tinyxpath
%patch3 -p1 -b.openzwave
#%patch4 -p1 -b.openzwave-Dev
%patch5 -p1 -b.python
%patch6 -p1
%patch7 -p1
rm -f hardware/openzwave/*.h
rm -rf hardware/openzwave/aes
rm -rf hardware/openzwave/command_classes
rm -rf hardware/openzwave/platform
rm -rf hardware/openzwave/value_classes
rm -rf sqlite/
rm -rf tinyxpath/

%build
install -d build && cd build
%cmake \
	-DUSE_OPENSSL_STATIC=NO \
	-DUSE_STATIC_LIBSTDCXX=NO \
	-DUSE_STATIC_OPENZWAVE=NO \
	-DUSE_BUILTIN_LUA=NO \
	-DUSE_BUILTIN_MQTT=NO \
	-DUSE_BUILTIN_SQLITE=NO \
	-DUSE_BUILTIN_TINYXPATH=NO \
	-DUSE_STATIC_BOOST=NO \
	-DCMAKE_INSTALL_PREFIX=%{_datadir}/%{name} \
	..

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} -C build install \
      DESTDIR=$RPM_BUILD_ROOT

# remove docs, we grab them in files below
rm -f $RPM_BUILD_ROOT%{_datadir}/%{name}/*.txt

# move binary to standard directory
install -d $RPM_BUILD_ROOT%{_bindir}/
mv $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name} $RPM_BUILD_ROOT%{_bindir}/

# install systemd service and config
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/
install -d $RPM_BUILD_ROOT%{systemdunitdir}/
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{systemdunitdir}/
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

# create database/ssl cert directory
install -d $RPM_BUILD_ROOT%{_sharedstatedir}/%{name}/

# Disable the app's self-update script

# Unbundle DroidSans.ttf
rm -f $RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/elemental/fonts/DroidSans.ttf
ln -s /usr/share/fonts/TTF/DroidSans.ttf \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/elemental/fonts/
rm -f $RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element-light/fonts/DroidSans.ttf
ln -s /usr/share/fonts/TTF/DroidSans.ttf \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element-light/fonts/
rm -f $RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element-dark/fonts/DroidSans.ttf
ln -s /usr/share/fonts/TTF/DroidSans.ttf \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element-dark/fonts/

# OpenZWave Control Panel temp file
ln -s %{_sharedstatedir}/%{name}/ozwcp.poll.XXXXXX.xml \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/ozwcp.poll.XXXXXX.xml

%clean
rm -rf $RPM_BUILD_ROOT

%pre
getent group domoticz >/dev/null || groupadd -r domoticz
getent passwd domoticz >/dev/null || \
useradd -r -g domoticz -d %{_datadir}/%{name} -s /sbin/nologin \
-c "Domoticz Home Automation Server" domoticz
# For OpenZWave USB access (/dev/ttyACM#)
usermod -G domoticz,dialout domoticz

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%defattr(644,root,root,755)
%doc License.txt
%doc README.md History.txt
%attr(755,root,root) %{_bindir}/%{name}
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%{_datadir}/%{name}/
%attr(755,domoticz,domoticz) %{_sharedstatedir}/%{name}/
%{systemdunitdir}/%{name}.service
