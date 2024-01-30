Summary:	Open source Home Automation System
Name:		domoticz
Version:	2024.4
Release:	1
License:	GPLv3+ and ASL 2.0 and Boost and BSD and MIT
Group:		Base
URL:		http://www.domoticz.com
Source0:	https://github.com/domoticz/domoticz/archive/%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	23f0aab1b388076394530d769defc710
Source1:	%{name}.service
Source2:	%{name}.conf
# Use system tinyxpath (https://github.com/domoticz/domoticz/pull/1759)
Patch0:		%{name}-tinyxpath.patch
# Fix python detection (https://github.com/domoticz/domoticz/pull/1749)
Patch1:		%{name}-python.patch
Patch2:		no-git.patch
Patch3:		%{name}-no_updates.patch
Patch4:		config.patch
BuildRequires:	boost-devel >= 1.66.0
BuildRequires:	cereal-devel
BuildRequires:	cmake >= 3.16.0
BuildRequires:	curl-devel
BuildRequires:	jsoncpp-devel
BuildRequires:	libmosquitto-devel
BuildRequires:	libopenzwave-devel >= 1.5.0
BuildRequires:	libstdc++-devel >= 6:4.9
BuildRequires:	libusb-compat-devel
BuildRequires:	linux-libc-headers
BuildRequires:	lua53-devel
BuildRequires:	minizip-devel
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig
BuildRequires:	python3 >= 1:3.4
BuildRequires:	python3-devel >= 1:3.4
BuildRequires:	rpmbuild(macros) >= 1.644
BuildRequires:	sqlite3-devel
BuildRequires:	tinyxml-devel
BuildRequires:	tinyxpath-devel
BuildRequires:	zlib-devel
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires(post,preun,postun):	systemd-units >= 38
Requires:	fonts-TTF-Google-Droid
Requires:	fonts-TTF-OpenSans
Requires:	libopenzwave >= 1.5.0
Requires:	setup >= 2.10.1
Suggests:	python3-libs
Provides:	group(domoticz)
Provides:	user(domoticz)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Domoticz is a Home Automation System that lets you monitor and
configure various devices like: Lights, Switches, various
sensors/meters like Temperature, Rain, Wind, UV, Electra, Gas, Water
and much more. Notifications/Alerts can be sent to any mobile device

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

APPVERSION="%{version}"
echo "#define APPVERSION ${APPVERSION##*.}" > appversion.h
echo '#define APPHASH "%{snap}"' >> appversion.h
APPDATE=$(date --date="%{date}" "+%s")
echo "#define APPDATE ${APPDATE}" >> appversion.h

%{__rm} -r extern tinyxpath

%build
install -d build && cd build
export CXXFLAGS="%{rpmcxxflags} -DPYTHON_LIBDIR=\\\"%{_libdir}\\\""
%cmake \
	-DUSE_BUILTIN_JSONCPP=NO \
	-DUSE_BUILTIN_MINIZIP=NO \
	-DUSE_BUILTIN_MQTT=NO \
	-DUSE_BUILTIN_SQLITE=NO \
	-DUSE_BUILTIN_TINYXPATH=NO \
	-DUSE_LUA_STATIC=NO \
	-DUSE_OPENSSL_STATIC=NO \
	-DUSE_STATIC_BOOST=NO \
	-DUSE_STATIC_LIBSTDCXX=NO \
	-DUSE_STATIC_OPENZWAVE=NO \
	-DFORCE_WITH_GPIO:BOOL=TRUE \
	-DCMAKE_INSTALL_PREFIX=%{_datadir}/%{name} \
	..

%{__make}

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_bindir},%{_sysconfdir}/{domoticz,sysconfig},%{systemdunitdir},%{_sharedstatedir}/%{name}}

# remove docs, we grab them in files below
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/*.txt

# move binary to standard directory
mv $RPM_BUILD_ROOT%{_datadir}/%{name}/%{name} $RPM_BUILD_ROOT%{_bindir}

sed -e 's#@DOMOTICZ_DIR@#%{_datadir}/%{name}#g' %{SOURCE1} > $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
sed -e 's#@DOMOTICZ_DIR@#%{_datadir}/%{name}#g' scripts/domoticz.conf > $RPM_BUILD_ROOT%{_sysconfdir}/domoticz/domoticz.conf
sed -e 's#@DOMOTICZ_CONF_DIR@#%{_sysconfdir}/%{name}#' %{SOURCE2} > $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}

# Unbundle DroidSans.ttf
%{__rm} $RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element{al,-light,-dark}/fonts/{Droid,Open}Sans.ttf
ln -s %{_fontsdir}/TTF/DroidSans.ttf \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/elemental/fonts
ln -s %{_fontsdir}/TTF/OpenSans-Regular.ttf \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/elemental/fonts/OpenSans.ttf
ln -s %{_fontsdir}/TTF/DroidSans.ttf \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element-light/fonts
ln -s %{_fontsdir}/TTF/OpenSans-Regular.ttf \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element-light/fonts/OpenSans.ttf
ln -s %{_fontsdir}/TTF/DroidSans.ttf \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element-dark/fonts
ln -s %{_fontsdir}/TTF/OpenSans-Regular.ttf \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/www/styles/element-dark/fonts/OpenSans.ttf

# OpenZWave Control Panel temp file
ln -s %{_sharedstatedir}/%{name}/ozwcp.poll.XXXXXX.xml \
	$RPM_BUILD_ROOT%{_datadir}/%{name}/ozwcp.poll.XXXXXX.xml

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 342 domoticz
%useradd -u 342 -r -d %{_datadir} -s /bin/false -c "Domoticz Home Automation Server" -G dialout,i2c -g domoticz domoticz

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove domoticz
	%groupremove domoticz
fi
%systemd_reload

%triggerpostun -- domoticz < 2022.1
if [ -f /etc/sysconfig/domoticz.rpmnew ] && [ -f /etc/sysconfig/domoticz ] && ! grep -q '^DOMOTICZ_CONF=' /etc/sysconfig/domoticz; then
	(
	. /etc/sysconfig/domoticz
	for c in WWW_PORT:http_port SSL_PORT:ssl_port SSLCERT:ssl_cert SSLPASS:ssl_pass SSLMETHOD:ssl_method SSLOPTIONS:ssl_options SSLDHPARAM:ssl_dhparam WWW_ROOT:http_root DBASE:dbase_file USERDATA:userdata_path LOG:log_file; do
		cn_before=${c%:*}
		cn_after=${c#*:}
		eval cn_value=\"\$$cn_before\"
		test -n "$cn_value" && sed -i -e "s|^[[:space:]#]*$cn_after=.*|$cn_after=$cn_value|" %{_sysconfdir}/%{name}/%{name}.conf
	done
	)
	mv -f /etc/sysconfig/domoticz{,.rpmsave}
	mv /etc/sysconfig/domoticz{.rpmnew,}
fi

%files
%defattr(644,root,root,755)
%doc License.txt README.md History.txt
%attr(755,root,root) %{_bindir}/%{name}
%dir %attr(750,domoticz,domoticz) %{_sysconfdir}/%{name}
%attr(640,domoticz,domoticz) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/%{name}
%{_datadir}/%{name}
%dir %attr(750,domoticz,domoticz) %{_sharedstatedir}/%{name}
%{systemdunitdir}/%{name}.service
