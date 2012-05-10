#Module-Specific definitions
%define mod_name mod_php
%define load_order 170
%define extname apache2handler

%define epoch 3
%define major 5
%define libname %mklibname php5_common %{major}
%define apache_version 2.4.0
%define php_version %{version}

Summary:	The PHP HTML-embedded scripting language for use with apache
Name:		apache-%{mod_name}
Version:	5.4.3
Release:	1
Group:		System/Servers
License:	PHP License
URL:		http://www.php.net/
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires:	%{libname} >= %{epoch}:%{php_version}
Requires:	apache-base >= %{apache_version}
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
Epoch:		%{epoch}

%description
PHP5 is an HTML-embedded scripting language. PHP5 attempts to make it easy for
developers to write dynamically generated web pages. PHP5 also offers built-in
database integration for several commercial and non-commercial database
management systems, so writing a database-enabled web page with PHP5 is fairly
simple. The most common use of PHP coding is probably as a replacement for CGI
scripts. The %{name} module enables the apache web server to understand
and process the embedded PHP language in web pages.

This package contains PHP version 5. You'll also need to install the apache web
server.

%prep

%setup -c -T
cp -dpR %{_usrsrc}/php-devel/sapi/%{extname}/* .
cp %{_usrsrc}/php-devel/internal_functions.c .
cp %{_includedir}/php/ext/date/lib/timelib_config.h .

# drop php5 here
perl -pi -e "s|php5_module|php_module|g" *
cp mod_php5.c mod_php.c

# strip away annoying ^M
find -type f -exec dos2unix {} \;

%build

apxs \
    `php-config --includes` \
    `apr-1-config --link-ld --libs` \
    `xml2-config --cflags` \
    -I%{_usrsrc}/php-devel \
    -I. -lphp5_common \
    -c mod_php.c sapi_apache2.c apache_config.c \
    php_functions.c internal_functions.c

%install

install -d %{buildroot}%{_libdir}/apache
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 .libs/*.so %{buildroot}%{_libdir}/apache/

cat > %{buildroot}%{_sysconfdir}/httpd/modules.d/%{load_order}_%{mod_name}.conf << EOF
LoadModule php_module %{_libdir}/apache/%{mod_name}.so

AddType application/x-httpd-php .php
AddType application/x-httpd-php .phtml
AddType application/x-httpd-php-source .phps

DirectoryIndex index.php index.phtml
EOF

%post
/bin/systemctl daemon-reload >/dev/null 2>&1 || :

%postun
if [ "$1" = "0" ]; then
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%files
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/*.conf
%attr(0755,root,root) %{_libdir}/apache/*.so
