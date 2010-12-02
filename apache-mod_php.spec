#Module-Specific definitions
%define mod_name mod_php
%define mod_conf 70_%{mod_name}.conf
%define mod_so %{mod_name}5.so
%define extname apache2handler

%define epoch 3
%define major 5
%define libname %mklibname php5_common %{major}
%define apache_version 2.2.8
%define php_version %{version}

Summary:	The PHP5 HTML-embedded scripting language for use with apache
Name:		apache-%{mod_name}
Version:	5.3.4
Release:	%mkrel 0.0.RC1.3
Group:		System/Servers
License:	PHP License
URL:		http://www.php.net/
Source1:	%{mod_conf}
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires:	%{libname} >= %{epoch}:%{php_version}
Requires:	apache-base >= %{apache_version}
Requires:	apache-conf >= %{apache_version}
Requires:	apache-modules >= %{apache_version}
Requires:	apache-mpm >= %{apache_version}
Requires:	php-ctype >= %{epoch}:%{php_version}
Requires:	php-filter >= %{epoch}:%{php_version}
Requires:	php-ftp >= %{epoch}:%{php_version}
Requires:	php-gettext >= %{epoch}:%{php_version}
Requires:	php-hash >= %{epoch}:%{php_version}
Requires:	php-ini >= %{php_version}
Requires:	php-json >= %{epoch}:%{php_version}
Requires:	php-openssl >= %{epoch}:%{version}
Requires:	php-pcre >= %{epoch}:%{php_version}
Requires:	php-posix >= %{epoch}:%{php_version}
Requires:	php-session >= %{epoch}:%{php_version}
Requires:	php-suhosin >= 0.9.29
Requires:	php-sysvsem >= %{epoch}:%{php_version}
Requires:	php-sysvshm >= %{epoch}:%{php_version}
Requires:	php-tokenizer >= %{epoch}:%{php_version}
Requires:	php-xmlreader >= %{epoch}:%{php_version}
Requires:	php-xmlwriter >= %{epoch}:%{php_version}
Requires:	php-zlib >= %{epoch}:%{php_version}
Requires:	php-xml >= %{epoch}:%{version}
BuildRequires:	apache-devel >= %{apache_version}
BuildRequires:	php-devel >= %{epoch}:%{php_version}
BuildRequires:	dos2unix
Provides:	php mod_php
Obsoletes:	php mod_php
Conflicts:	apache-mpm-worker >= %{apache_version}
Conflicts:	apache-mpm-event >= %{apache_version}
Requires:	php-timezonedb >= 3:2009.10
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Epoch:		%{epoch}

%description
PHP5 is an HTML-embedded scripting language. PHP5 attempts to make it easy for
developers to write dynamically generated web pages. PHP5 also offers built-in
database integration for several commercial and non-commercial database
management systems, so writing a database-enabled web page with PHP5 is fairly
simple. The most common use of PHP coding is probably as a replacement for CGI
scripts. The %{name} module enables the apache web server to understand and
process the embedded PHP language in web pages.

This package contains PHP version 5. You'll also need to install the apache web
server.

%prep

%setup -c -T
cp -dpR %{_usrsrc}/php-devel/sapi/%{extname}/* .
cp %{_usrsrc}/php-devel/internal_functions.c .
cp %{_includedir}/php/ext/date/lib/timelib_config.h .

# strip away annoying ^M
find -type f -exec dos2unix -U {} \;

cp %{SOURCE1} %{mod_conf}

%build

%{_sbindir}/apxs \
    `php-config --includes` \
    `apr-1-config --link-ld --libs` \
    `xml2-config --cflags` \
    -I%{_usrsrc}/php-devel \
    -I. -lphp5_common \
    -c mod_php5.c sapi_apache2.c apache_config.c \
    php_functions.c internal_functions.c

%install
rm -rf %{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}
