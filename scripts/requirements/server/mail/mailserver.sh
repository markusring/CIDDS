#!/bin/bash

#update and upgrade
apt-get -y update
apt-get -y upgrade

echo mysql-server mysql-server/root_password select PWfMS2015 | debconf-set-selections
echo mysql-server mysql-server/root_password_again select PWfMS2015 | debconf-set-selections

echo postfix postfix/mailname string mailserver.com | debconf-set-selections
echo postfix postfix/main_mailer_type string 'Internet Site' | debconf-set-selections

# Define the packets to install with apt-get 
declare -a packagesAptGet=("curl" "whois" "mysql-server" "php5" "php5-imap" "php5-mysql" "apache2" "dovecot-core" "dovecot-mysql" "dovecot-imapd" "dovecot-pop3d" "postfix" "postfix-mysql")

# Install all predefined packages 
for package in "${packagesAptGet[@]}"
do
	echo "Looking for package $package."
	until dpkg -s $package | grep -q Status;
	do
	    echo "$package not found. Installing..."
	    apt-get --force-yes --yes install $package
	done
	echo "$package found."
done

apt-get -y update
apt-get -y upgrade

#postfix configuration
mysql -uroot --password=PWfMS2015 -e "CREATE DATABASE postfixdb; GRANT ALL PRIVILEGES ON postfixdb.* TO 'postfix'@'localhost' IDENTIFIED BY 'MYSQLPW'; FLUSH PRIVILEGES;"
cd /var/www
wget --content-disposition https://sourceforge.net/projects/postfixadmin/files/postfixadmin/postfixadmin-3.0.2/postfixadmin-3.0.2.tar.gz/download
tar xfvz postfixadmin-*.tar.gz
mv postfixadmin*/ postfixadmin
chown www-data:www-data -R postfixadmin
cd postfixadmin
#??
#sed -i "s/change-this-to-your.domain.tld/domain.tld/g" config.inc.php
#write config.inc.php, end at line 648
cat > config.inc.php <<EOF
<?php
/**
 * Postfix Admin
 *
 * LICENSE
 * This source file is subject to the GPL license that is bundled with
 * this package in the file LICENSE.TXT.
 *
 * Further details on the project are available at http://postfixadmin.sf.net
 *
 * @version \$Id: config.inc.php 1694 2014-10-07 16:11:49Z christian_boltz \$
 * @license GNU GPL v2 or later.
 *
 * File: config.inc.php
 * Contains configuration options.
 */

/*****************************************************************
 *  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
 * You have to set \$CONF['configured'] = true; before the
 * application will run!
 * Doing this implies you have changed this file as required.
 * i.e. configuring database etc; specifying setup.php password etc.
 */
\$CONF['configured'] = true;

// In order to setup Postfixadmin, you MUST specify a hashed password here.
// To create the hash, visit setup.php in a browser and type a password into the field,
// on submission it will be echoed out to you as a hashed value.
\$CONF['setup_password'] = '4b5da2c6d9d2b9eabdde6f86616154ce:12ff46c3f988ee2253078eb1315c04de74031684';

// Language config
// Language files are located in './languages', change as required..
\$CONF['default_language'] = 'de';

// Hook to override or add translations in \$PALANG
// Set to the function name you want to use as hook function (see language_hook example function below)
\$CONF['language_hook'] = '';

/*
    language_hook example function

    Called if \$CONF['language_hook'] == '<name_of_the_function>'
    Allows to add or override \$PALANG interface texts.

    If you add new texts, please always prefix them with 'x_' (for example
    \$PALANG['x_mytext'] = 'foo') to avoid they clash with texts that might be
    added to languages/*.lang in future versions of PostfixAdmin.

    Please also make sure that all your added texts are included in all
    sections - that includes all 'case "XY":' sections and the 'default:'
    section (for users that don't have any of the languages specified
    in the 'case "XY":' section).
    Usually the 'default:' section should contain english text.

    If you modify an existing text/translation, please consider to report it
    to the bugtracker on http://sf.net/projects/postfixadmin so that all users
    can benefit from the corrected text/translation.
    Returns: modified \$PALANG array
*/
/*
function language_hook(\$PALANG, \$language) {
    switch (\$language) {
        case "de":
            \$PALANG['x_whatever'] = 'foo';
            break;
        case "fr":
            \$PALANG['x_whatever'] = 'bar';
            break;
        default:
            \$PALANG['x_whatever'] = 'foobar';
    }

    return \$PALANG;
}
*/
// Database Config
// mysql = MySQL 3.23 and 4.0, 4.1 or 5
// mysqli = MySQL 4.1+
// pgsql = PostgreSQL
\$CONF['database_type'] = 'mysql';
\$CONF['database_host'] = 'localhost';
\$CONF['database_user'] = 'postfix';
\$CONF['database_password'] = 'MYSQLPW';
\$CONF['database_name'] = 'postfixdb';
// If you need to specify a different port for a MYSQL database connection, use e.g.
//   \$CONF['database_host'] = '172.30.33.66:3308';
// If you need to specify a different port for POSTGRESQL database connection
//   uncomment and change the following
// \$CONF['database_port'] = '5432';

// Here, if you need, you can customize table names.
\$CONF['database_prefix'] = '';
\$CONF['database_tables'] = array (
    'admin' => 'admin',
    'alias' => 'alias',
    'alias_domain' => 'alias_domain',
    'config' => 'config',
    'domain' => 'domain',
    'domain_admins' => 'domain_admins',
    'fetchmail' => 'fetchmail',
    'log' => 'log',
    'mailbox' => 'mailbox',
    'vacation' => 'vacation',
    'vacation_notification' => 'vacation_notification',
    'quota' => 'quota',
        'quota2' => 'quota2',
);
// Site Admin
// Define the Site Admin's email address below.
// This will be used to send emails from to create mailboxes and
// from Send Email / Broadcast message pages.
// Leave blank to send email from the logged-in Admin's Email address.
\$CONF['admin_email'] = '';

// Mail Server
// Hostname (FQDN) of your mail server.
// This is used to send email to Postfix in order to create mailboxes.
\$CONF['smtp_server'] = 'localhost';
\$CONF['smtp_port'] = '25';

// Encrypt
// In what way do you want the passwords to be crypted?
// md5crypt = internal postfix admin md5
// md5 = md5 sum of the password
// system = whatever you have set as your PHP system default
// cleartext = clear text passwords (ouch!)
// mysql_encrypt = useful for PAM integration
// authlib = support for courier-authlib style passwords
// dovecot:CRYPT-METHOD = use dovecotpw -s 'CRYPT-METHOD'. Example: dovecot:CRAM-MD5
//   (WARNING: don't use dovecot:* methods that include the username in the hash - you won't be able to login to PostfixAdmin in this case)
\$CONF['encrypt'] = 'md5crypt';

// In what flavor should courier-authlib style passwords be encrypted?
// md5 = {md5} + base64 encoded md5 hash
// md5raw = {md5raw} + plain encoded md5 hash
// SHA = {SHA} + base64-encoded sha1 hash
// crypt = {crypt} + Standard UNIX DES-encrypted with 2-character salt
\$CONF['authlib_default_flavor'] = 'md5raw';

// If you use the dovecot encryption method: where is the dovecotpw binary located?
// for dovecot 1.x
// \$CONF['dovecotpw'] = "/usr/sbin/dovecotpw";
// for dovecot 2.x (dovecot 2.0.0 - 2.0.7 is not supported!)
\$CONF['dovecotpw'] = "/usr/sbin/doveadm pw";

// Password validation
// New/changed passwords will be validated using all regular expressions in the array.
// If a password doesn't match one of the regular expressions, the corresponding
// error message from \$PALANG (see languages/*) will be displayed.
// See http://de3.php.net/manual/en/reference.pcre.pattern.syntax.php for details
// about the regular expression syntax.
// If you need custom error messages, you can add them using \$CONF['language_hook'].
// If a \$PALANG text contains a %s, you can add its value after the \$PALANG key
// (separated with a space).
\$CONF['password_validation'] = array(
#    '/regular expression/' => '\$PALANG key (optional: + parameter)',
    '/.{5}/'                => 'password_too_short 5',      # minimum length 5 characters
    '/([a-zA-Z].*){3}/'     => 'password_no_characters 3',  # must contain at least 3 characters
    '/([0-9].*){2}/'        => 'password_no_digits 2',      # must contain at least 2 digits
);

// Generate Password
// Generate a random password for a mailbox or admin and display it.
// If you want to automagically generate passwords set this to 'YES'.
\$CONF['generate_password'] = 'NO';

// Show Password
// Always show password after adding a mailbox or admin.
// If you want to always see what password was set set this to 'YES'.
\$CONF['show_password'] = 'NO';
// Page Size
// Set the number of entries that you would like to see
// in one page.
\$CONF['page_size'] = '10';

// Default Aliases
// The default aliases that need to be created for all domains.
// You can specify the target address in two ways:
// a) a full mail address
// b) only a localpart ('postmaster' => 'admin') - the alias target will point to the same domain
\$CONF['default_aliases'] = array (
    'abuse' => 'abuse@domain.tld',
    'hostmaster' => 'hostmaster@domain.tld',
    'postmaster' => 'postmaster@domain.tld',
    'webmaster' => 'webmaster@domain.tld'
);
// Mailboxes
// If you want to store the mailboxes per domain set this to 'YES'.
// Examples:
//   YES: /usr/local/virtual/domain.tld/username@domain.tld
//   NO:  /usr/local/virtual/username@domain.tld
\$CONF['domain_path'] = 'YES';
// If you don't want to have the domain in your mailbox set this to 'NO'.
// Examples:
//   YES: /usr/local/virtual/domain.tld/username@domain.tld
//   NO:  /usr/local/virtual/domain.tld/username
// Note: If \$CONF['domain_path'] is set to NO, this setting will be forced to YES.
\$CONF['domain_in_mailbox'] = 'NO';
// If you want to define your own function to generate a maildir path set this to the name of the function.
// Notes:
//   - this configuration directive will override both domain_path and domain_in_mailbox
//   - the maildir_name_hook() function example is present below, commented out
//   - if the function does not exist the program will default to the above domain_path and domain_in_mailbox settings
\$CONF['maildir_name_hook'] = 'NO';
/*
    maildir_name_hook example function

    Called when creating a mailbox if \$CONF['maildir_name_hook'] == '<name_of_the_function>'
    - allows for customized maildir paths determined by a custom function
    - the example below will prepend a single-character directory to the
      beginning of the maildir, splitting domains more or less evenly over
      36 directories for improved filesystem performance with large numbers
      of domains.

    Returns: maildir path
    ie. I/example.com/user/
*/
/*
function maildir_name_hook(\$domain, \$user) {
    \$chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ";

    \$dir_index = hexdec(substr(md5(\$domain), 28)) % strlen(\$chars);
    \$dir = substr(\$chars, \$dir_index, 1);
    return sprintf("%s/%s/%s/", \$dir, \$domain, \$user);
}
*/

/*
    *_struct_hook - change, add or remove fields

    If you need additional fields or want to change or remove existing fields,
    you can write a hook function to modify \$struct in the *Handler classes.

    The edit form will automatically be updated according to the modified
    \$struct. The list page is not yet updated automatically.

    You can define one hook function per class, named like the primary database
    table of that class.
    The hook function is called with \$struct as parameter and must return the
    modified \$struct.

    Note: Adding a field to \$struct adds the handling of this field in
    PostfixAdmin, but it does not create it in the database. You have to do
    that yourself.
    Please follow the naming policy for custom database fields and tables on
    http://sourceforge.net/apps/mediawiki/postfixadmin/index.php?title=Custom_fields
    to avoid clashes with future versions of PostfixAdmin.
    See initStruct() in the *Handler class for the default \$struct.
    See pacol() in functions.inc.php for the available flags on each column.

    Example:

    function x_struct_admin_modify(\$struct) {
        \$struct['superadmin']['editable'] = 0;          # make the 'superadmin' flag read-only
        \$struct['superadmin']['display_in_form'] = 0;   # don't display the 'superadmin' flag in edit form
        \$struct['x_newfield'] = pacol( [...] );        # additional field 'x_newfield'
        return \$struct; # important!
    }
    \$CONF['admin_struct_hook'] = 'x_struct_admin_modify';
*/
\$CONF['admin_struct_hook']          = '';
\$CONF['domain_struct_hook']         = '';
\$CONF['alias_struct_hook']          = '';
\$CONF['mailbox_struct_hook']        = '';
\$CONF['alias_domain_struct_hook']   = '';


// Default Domain Values
// Specify your default values below. Quota in MB.
\$CONF['aliases'] = '10';
\$CONF['mailboxes'] = '10';
\$CONF['maxquota'] = '10';
\$CONF['domain_quota_default'] = '2048';

// Quota
// When you want to enforce quota for your mailbox users set this to 'YES'.
\$CONF['quota'] = 'NO';
// If you want to enforce domain-level quotas set this to 'YES'.
\$CONF['domain_quota'] = 'YES';
// You can either use '1024000' or '1048576'
\$CONF['quota_multiplier'] = '1024000';

// Transport
// If you want to define additional transport options for a domain set this to 'YES'.
// Read the transport file of the Postfix documentation.
\$CONF['transport'] = 'NO';
// Transport options
// If you want to define additional transport options put them in array below.
\$CONF['transport_options'] = array (
    'virtual',  // for virtual accounts
    'local',    // for system accounts
    'relay'     // for backup mx
);
// Transport default
// You should define default transport. It must be in array above.
\$CONF['transport_default'] = 'virtual';


//
//
// Virtual Vacation Stuff
//
//

// If you want to use virtual vacation for you mailbox users set this to 'YES'.
// NOTE: Make sure that you install the vacation module. (See VIRTUAL-VACATION/)
\$CONF['vacation'] = 'NO';

// This is the autoreply domain that you will need to set in your Postfix
// transport maps to handle virtual vacations. It does not need to be a
// real domain (i.e. you don't need to setup DNS for it).
// This domain must exclusively be used for vacation. Do NOT use it for "normal" mail addresses.
\$CONF['vacation_domain'] = 'autoreply.domain.tld';

// Vacation Control
// If you want users to take control of vacation set this to 'YES'.
\$CONF['vacation_control'] ='YES';

// Vacation Control for admins
// Set to 'YES' if your domain admins should be able to edit user vacation.
\$CONF['vacation_control_admin'] = 'YES';
// ReplyType options
// If you want to define additional reply options put them in array below.
// The array has the format   seconds between replies => \$PALANG text
// Special values for seconds are:
// 0 => only reply to the first mail while on vacation
// 1 => reply on every mail
\$CONF['vacation_choice_of_reply'] = array (
   0 => 'reply_once',        // Sends only Once the message during Out of Office
   # considered annoying - only send a reply on every mail if you really need it
   # 1 => 'reply_every_mail',       // Reply on every email
   60*60 *24*7 => 'reply_once_per_week'        // Reply if last autoreply was at least a week ago
);
//
// End Vacation Stuff.
//

// Users Control for Domain Admin
// Set to "Yes" if your domain admins schould be able to  edit  field userscontrole in  table domain
// Userscontrol is edited in admin_create-domain.tpl and admin_edit-domain.tpl
// Userscontrol is default set  to  on when creating a domain
\$CONF['users_domain_controle'] = 'YES';


// Alias Control
// Postfix Admin inserts an alias in the alias table for every mailbox it creates.
// The reason for this is that when you want catch-all and normal mailboxes
// to work you need to have the mailbox replicated in the alias table.
// If you want to take control of these aliases as well set this to 'YES'.

// Alias control for superadmins
\$CONF['alias_control'] = 'YES';

// Alias Control for domain admins
\$CONF['alias_control_admin'] = 'YES';

// Special Alias Control
// Set to 'NO' if your domain admins shouldn't be able to edit the default aliases
// as defined in \$CONF['default_aliases']
\$CONF['special_alias_control'] = 'NO';

// Alias Goto Field Limit
// Set the max number of entries that you would like to see
// in one 'goto' field in overview, the rest will be hidden and "[and X more...]" will be added.
// '0' means no limits.
\$CONF['alias_goto_limit'] = '0';

// Alias Domains
// Alias domains allow to "mirror" aliases and mailboxes to another domain. This makes
// configuration easier if you need the same set of aliases on multiple domains, but
// also requires postfix to do more database queries.
// Note: If you update from 2.2.x or earlier, you will have to update your postfix configuration.
// Set to 'NO' to disable alias domains.
\$CONF['alias_domain'] = 'YES';

// Backup
// If you don't want backup tab set this to 'NO';
\$CONF['backup'] = 'NO';

// Send Mail
// If you don't want sendmail tab set this to 'NO';
\$CONF['sendmail'] = 'YES';

// Logging
// If you don't want logging set this to 'NO';
\$CONF['logging'] = 'YES';
// Fetchmail
// If you don't want fetchmail tab set this to 'NO';
\$CONF['fetchmail'] = 'YES';

// fetchmail_extra_options allows users to specify any fetchmail options and any MDA
// (it will even accept 'rm -rf /' as MDA!)
// This should be set to NO, except if you *really* trust *all* your users.
\$CONF['fetchmail_extra_options'] = 'NO';

// Header
\$CONF['show_header_text'] = 'NO';
\$CONF['header_text'] = ':: Postfix Admin ::';

// Footer
// Below information will be on all pages.
// If you don't want the footer information to appear set this to 'NO'.
\$CONF['show_footer_text'] = 'YES';
\$CONF['footer_text'] = 'Return to domain.tld';
\$CONF['footer_link'] = 'http://domain.tld';
// MOTD ("Motto of the day")
// You can display a MOTD below the menu on all pages.
// This can be configured seperately for users, domain admins and superadmins
\$CONF['motd_user'] = '';
\$CONF['motd_admin'] = '';
\$CONF['motd_superadmin'] = '';

// Welcome Message
// This message is send to every newly created mailbox.
// Change the text between EOM.
\$CONF['welcome_text'] = <<<EOM
Hi,

Welcome to your new account.
EOM;

// When creating mailboxes or aliases, check that the domain-part of the
// address is legal by performing a name server look-up.
\$CONF['emailcheck_resolve_domain']='YES';


// Optional:
// Analyze alias gotos and display a colored block in the first column
// indicating if an alias or mailbox appears to deliver to a non-existent
// account.  Also, display indications, for POP/IMAP mailboxes and
// for custom destinations (such as mailboxes that forward to a UNIX shell
// account or mail that is sent to a MS exchange server, or any other
// domain or subdomain you use)
// See http://www.w3schools.com/html/html_colornames.asp for a list of
// color names available on most browsers

//set to YES to enable this feature
\$CONF['show_status']='YES';
//display a guide to what these colors mean
\$CONF['show_status_key']='YES';
// 'show_status_text' will be displayed with the background colors
// associated with each status, you can customize it here
\$CONF['show_status_text']='&nbsp;&nbsp;';
// show_undeliverable is useful if most accounts are delivered to this
// postfix system.  If many aliases and mailboxes are forwarded
// elsewhere, you will probably want to disable this.
\$CONF['show_undeliverable']='YES';
\$CONF['show_undeliverable_color']='tomato';
// mails to these domains will never be flagged as undeliverable
\$CONF['show_undeliverable_exceptions']=array("unixmail.domain.ext","exchangeserver.domain.ext");
\$CONF['show_popimap']='YES';
\$CONF['show_popimap_color']='darkgrey';
// you can assign special colors to some domains. To do this,
// - add the domain to show_custom_domains
// - add the corresponding color to show_custom_colors
\$CONF['show_custom_domains']=array("subdomain.domain.ext","domain2.ext");
\$CONF['show_custom_colors']=array("lightgreen","lightblue");
// If you use a recipient_delimiter in your postfix config, you can also honor it when aliases are checked.
// Example: \$CONF['recipient_delimiter'] = "+";
// Set to "" to disable this check.
\$CONF['recipient_delimiter'] = "";

// Optional:
// Script to run after creation of mailboxes.
// Note that this may fail if PHP is run in "safe mode", or if
// operating system features (such as SELinux) or limitations
// prevent the web-server from executing external scripts.
// Parameters: (1) username (2) domain (3) maildir (4) quota
// \$CONF['mailbox_postcreation_script']='sudo -u courier /usr/local/bin/postfixadmin-mailbox-postcreation.sh';
\$CONF['mailbox_postcreation_script'] = '';

// Optional:
// Script to run after alteration of mailboxes.
// Note that this may fail if PHP is run in "safe mode", or if
// operating system features (such as SELinux) or limitations
// prevent the web-server from executing external scripts.
// Parameters: (1) username (2) domain (3) maildir (4) quota
// \$CONF['mailbox_postedit_script']='sudo -u courier /usr/local/bin/postfixadmin-mailbox-postedit.sh';
\$CONF['mailbox_postedit_script'] = '';

// Optional:
// Script to run after deletion of mailboxes.
// Note that this may fail if PHP is run in "safe mode", or if
// operating system features (such as SELinux) or limitations
// prevent the web-server from executing external scripts.
// Parameters: (1) username (2) domain
// \$CONF['mailbox_postdeletion_script']='sudo -u courier /usr/local/bin/postfixadmin-mailbox-postdeletion.sh';
\$CONF['mailbox_postdeletion_script'] = '';

// Optional:
// Script to run after creation of domains.
// Note that this may fail if PHP is run in "safe mode", or if
// operating system features (such as SELinux) or limitations
// prevent the web-server from executing external scripts.
// Parameters: (1) domain
//\$CONF['domain_postcreation_script']='sudo -u courier /usr/local/bin/postfixadmin-domain-postcreation.sh';
\$CONF['domain_postcreation_script'] = '';

// Optional:
// Script to run after deletion of domains.
// Note that this may fail if PHP is run in "safe mode", or if
// operating system features (such as SELinux) or limitations
// prevent the web-server from executing external scripts.
// Parameters: (1) domain
// \$CONF['domain_postdeletion_script']='sudo -u courier /usr/local/bin/postfixadmin-domain-postdeletion.sh';
\$CONF['domain_postdeletion_script'] = '';

// Optional:
// Sub-folders which should automatically be created for new users.
// The sub-folders will also be subscribed to automatically.
// Will only work with IMAP server which implement sub-folders.
// Will not work with POP3.
// If you define create_mailbox_subdirs, then the
// create_mailbox_subdirs_host must also be defined.
//
// \$CONF['create_mailbox_subdirs']=array('Spam');
\$CONF['create_mailbox_subdirs'] = array();
\$CONF['create_mailbox_subdirs_host']='localhost';
//
// Specify '' for Dovecot and 'INBOX.' for Courier.
\$CONF['create_mailbox_subdirs_prefix']='INBOX.';

// Optional:
// Show used quotas from Dovecot dictionary backend in virtual
// mailbox listing.
// See: DOCUMENTATION/DOVECOT.txt
//      http://wiki.dovecot.org/Quota/Dict
//
\$CONF['used_quotas'] = 'NO';

// if you use dovecot >= 1.2, set this to yes.
// Note about dovecot config: table "quota" is for 1.0 & 1.1, table "quota2" is for dovecot 1.2 and newer
\$CONF['new_quota_table'] = 'YES';

//
// Normally, the TCP port number does not have to be specified.
// \$CONF['create_mailbox_subdirs_hostport']=143;
//
// If you have trouble connecting to the IMAP-server, then specify
// a value for \$CONF['create_mailbox_subdirs_hostoptions']. These
// are some examples to experiment with:
// \$CONF['create_mailbox_subdirs_hostoptions']=array('notls');
// \$CONF['create_mailbox_subdirs_hostoptions']=array('novalidate-cert','norsh');
// See also the "Optional flags for names" table at
// http://www.php.net/manual/en/function.imap-open.php
\$CONF['create_mailbox_subdirs_hostoptions'] = array('');


// Theme Config
// Specify your own logo and CSS file
\$CONF['theme_logo'] = 'images/logo-default.png';
\$CONF['theme_css'] = 'css/default.css';
// If you want to customize some styles without editing the \$CONF['theme_css'] file,
// you can add a custom CSS file. It will be included after \$CONF['theme_css'].
\$CONF['theme_custom_css'] = '';

// XMLRPC Interface.
// This should be only of use if you wish to use e.g the
// Postfixadmin-Squirrelmail package
//  change to boolean true to enable xmlrpc
\$CONF['xmlrpc_enabled'] = false;

// If you want to keep most settings at default values and/or want to ensure
// that future updates work without problems, you can use a separate config
// file (config.local.php) instead of editing this file and override some
// settings there.
if (file_exists(dirname(__FILE__) . '/config.local.php')) {
    include(dirname(__FILE__) . '/config.local.php');
}

//
// END OF CONFIG FILE
//
/* vim: set expandtab softtabstop=4 tabstop=4 shiftwidth=4: */

EOF
#postfix user
groupadd -g 5000 vmail
useradd -g vmail -u 5000 vmail -d /var/vmail
mkdir /var/vmail
chown vmail:vmail /var/vmail
#cert
mkdir /etc/postfix/sslcert
cd /etc/postfix/sslcert
openssl req -new -newkey rsa:3072 -nodes -keyout mailserver.key -sha256 -days 730 -x509 -out mailserver.crt <<EOF
${DE}
${BY}
${Coburg}
${FHWi}
.
.
.
EOF
chmod go-rwx mailserver.key
#write /etc/postfix/main.cf
cd /etc/postfix/
cat > main.cf <<EOF
# See /usr/share/postfix/main.cf.dist for a commented, more complete version


# Debian specific:  Specifying a file name will cause the first
# line of that file to be used as the name.  The Debian default
# is /etc/mailname.
#myorigin = /etc/mailname

smtpd_banner = \$myhostname
biff = no

# appending .domain is the MUA's job.
append_dot_mydomain = no

# Uncomment the next line to generate "delayed mail" warnings
#delay_warning_time = 4h

readme_directory = no

# TLS parameters
smtpd_tls_cert_file=/etc/postfix/sslcert/mailserver.crt
smtpd_tls_key_file=/etc/postfix/sslcert/mailserver.key
smtpd_use_tls=yes
smtpd_tls_session_cache_database = btree:\${data_directory}/smtpd_scache

smtp_tls_cert_file = /etc/postfix/sslcert/mailserver.crt
Ösmtp_tls_key_file = /etc/postfix/sslcert/mailserver.key
smtp_tls_security_level=may
smtpd_tls_mandatory_protocols = !SSLv2, !SSLv3
smtp_tls_session_cache_database = btree:\${data_directory}/smtp_scache
tls_high_cipherlist=EDH+CAMELLIA:EDH+aRSA:EECDH+aRSA+AESGCM:EECDH+aRSA+SHA384:EECDH+aRSA+SHA256:EECDH:+CAMELLIA256:+AES256:+CAMELLIA128:+AES128:+SSLv3:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!DSS:!RC4:!SEED:!ECDSA:CAMELLIA256-SHA:AES256-SHA:CAMELLIA128-SHA:AES128-SHA

# See /usr/share/doc/postfix/TLS_README.gz in the postfix-doc package for
# information on enabling SSL in the smtp client.

smtpd_relay_restrictions = permit_mynetworks permit_sasl_authenticated defer_unauth_destination
myhostname = mailserver.novalocal
alias_maps = hash:/etc/aliases
alias_database = hash:/etc/aliases
myorigin = /etc/mailname
mydestination = mailserver.novalocal, localhost.novalocal, localhost
relayhost =
mynetworks = 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128
mailbox_size_limit = 0
recipient_delimiter = +
inet_interfaces = all

# a bit more spam protection
disable_vrfy_command = yes
# Authentification
smtpd_sasl_type=dovecot
smtpd_sasl_path=private/auth_dovecot
smtpd_sasl_auth_enable = yes
smtpd_sasl_authenticated_header = yes
broken_sasl_auth_clients = yes
proxy_read_maps = \$local_recipient_maps \$mydestination \$virtual_alias_maps \$virtual_alias_domains \$virtual_mailbox_maps \$virtual_mailbox_domains \$relay_recipient_maps \$relay_domains \$canonical_maps \$sender_canonical_maps \$recipient_canonical_maps \$relocated_maps \$transport_maps \$mynetworks \$smtpd_sender_login_maps
smtpd_sender_login_maps = proxy:mysql:/etc/postfix/mysql_sender_login_maps.cf
smtpd_sender_restrictions = reject_authenticated_sender_login_mismatch
                reject_unknown_sender_domain
                reject_unverified_sender
                permit_sasl_authenticated
smtpd_recipient_restrictions = permit_sasl_authenticated
                permit_mynetworks
                reject_rbl_client zen.spamhaus.org
                reject_unauth_destination
                reject_unknown_reverse_client_hostname
smtpd_data_restrictions = reject_unauth_pipelining
                permit
# Virtual mailboxes
#local_transport = virtual
virtual_alias_maps = proxy:mysql:/etc/postfix/mysql_virtual_alias_maps.cf
virtual_mailbox_base = /var/vmail/
virtual_mailbox_domains = proxy:mysql:/etc/postfix/mysql_virtual_domains_maps.cf
virtual_mailbox_maps = proxy:mysql:/etc/postfix/mysql_virtual_mailbox_maps.cf
virtual_minimum_uid = 104
virtual_uid_maps = static:5000
virtual_gid_maps = static:5000
virtual_transport = dovecot
dovecot_destination_recipient_limit = 1
EOF
#Writing /etc/postfix/master.cf
cat > master.cf <<EOF
#
# Postfix master process configuration file.  For details on the format
# of the file, see the master(5) manual page (command: "man 5 master" or
# on-line: http://www.postfix.org/master.5.html).
#
# Do not forget to execute "postfix reload" after editing this file.
#
# ==========================================================================
# service type  private unpriv  chroot  wakeup  maxproc command + args
#               (yes)   (yes)   (yes)   (never) (100)
# ==========================================================================
smtp      inet  n       -       -       -       -       smtpd
#smtp      inet  n       -       -       -       1       postscreen
#smtpd     pass  -       -       -       -       -       smtpd
#dnsblog   unix  -       -       -       -       0       dnsblog
#tlsproxy  unix  -       -       -       -       0       tlsproxy
#submission inet n       -       -       -       -       smtpd
#  -o syslog_name=postfix/submission
#  -o smtpd_tls_security_level=encrypt
#  -o smtpd_sasl_auth_enable=yes
#  -o smtpd_reject_unlisted_recipient=no
#  -o smtpd_client_restrictions=\$mua_client_restrictions
#  -o smtpd_helo_restrictions=\$mua_helo_restrictions
#  -o smtpd_sender_restrictions=\$mua_sender_restrictions
#  -o smtpd_recipient_restrictions=
#  -o smtpd_relay_restrictions=permit_sasl_authenticated,reject
#  -o milter_macro_daemon_name=ORIGINATING
#smtps     inet  n       -       -       -       -       smtpd
#  -o syslog_name=postfix/smtps
#  -o smtpd_tls_wrappermode=yes
#  -o smtpd_sasl_auth_enable=yes
#  -o smtpd_reject_unlisted_recipient=no
#  -o smtpd_client_restrictions=\$mua_client_restrictions
#  -o smtpd_helo_restrictions=\$mua_helo_restrictions
#  -o smtpd_sender_restrictions=\$mua_sender_restrictions
#  -o smtpd_recipient_restrictions=
#  -o smtpd_relay_restrictions=permit_sasl_authenticated,reject
#  -o milter_macro_daemon_name=ORIGINATING
#628       inet  n       -       -       -       -       qmqpd
pickup    unix  n       -       -       60      1       pickup
cleanup   unix  n       -       -       -       0       cleanup
qmgr      unix  n       -       n       300     1       qmgr
#qmgr     unix  n       -       n       300     1       oqmgr
tlsmgr    unix  -       -       -       1000?   1       tlsmgr
rewrite   unix  -       -       -       -       -       trivial-rewrite
bounce    unix  -       -       -       -       0       bounce
defer     unix  -       -       -       -       0       bounce
trace     unix  -       -       -       -       0       bounce
verify    unix  -       -       -       -       1       verify
flush     unix  n       -       -       1000?   0       flush
proxymap  unix  -       -       n       -       -       proxymap
proxywrite unix -       -       n       -       1       proxymap
smtp      unix  -       -       -       -       -       smtp
relay     unix  -       -       -       -       -       smtp
#       -o smtp_helo_timeout=5 -o smtp_connect_timeout=5
showq     unix  n       -       -       -       -       showq
error     unix  -       -       -       -       -       error
retry     unix  -       -       -       -       -       error
discard   unix  -       -       -       -       -       discard
local     unix  -       n       n       -       -       local
virtual   unix  -       n       n       -       -       virtual
lmtp      unix  -       -       -       -       -       lmtp
anvil     unix  -       -       -       -       1       anvil
scache    unix  -       -       -       -       1       scache
#
# ====================================================================
# Interfaces to non-Postfix software. Be sure to examine the manual
# pages of the non-Postfix software to find out what options it wants.
#
# Many of the following services use the Postfix pipe(8) delivery
# agent.  See the pipe(8) man page for information about \${recipient}
# and other message envelope options.
# ====================================================================
#
# maildrop. See the Postfix MAILDROP_README file for details.
# Also specify in main.cf: maildrop_destination_recipient_limit=1
#
maildrop  unix  -       n       n       -       -       pipe
  flags=DRhu user=vmail argv=/usr/bin/maildrop -d \${recipient}
#
# ====================================================================
#
# Recent Cyrus versions can use the existing "lmtp" master.cf entry.
#
# Specify in cyrus.conf:
#   lmtp    cmd="lmtpd -a" listen="localhost:lmtp" proto=tcp4
#
# Specify in main.cf one or more of the following:
#  mailbox_transport = lmtp:inet:localhost
#  virtual_transport = lmtp:inet:localhost
#
# ====================================================================
#
# Cyrus 2.1.5 (Amos Gouaux)
# Also specify in main.cf: cyrus_destination_recipient_limit=1
#
#cyrus     unix  -       n       n       -       -       pipe
#  user=cyrus argv=/cyrus/bin/deliver -e -r \${sender} -m \${extension} \${user}
#
# ====================================================================
# Old example of delivery via Cyrus.
#
#old-cyrus unix  -       n       n       -       -       pipe
#  flags=R user=cyrus argv=/cyrus/bin/deliver -e -m \${extension} \${user}
#
# ====================================================================
#
# See the Postfix UUCP_README file for configuration details.
#
uucp      unix  -       n       n       -       -       pipe
  flags=Fqhu user=uucp argv=uux -r -n -z -a\$sender - \$nexthop!rmail (\$recipient)
#
# Other external delivery methods.
#
ifmail    unix  -       n       n       -       -       pipe
  flags=F user=ftn argv=/usr/lib/ifmail/ifmail -r \$nexthop (\$recipient)
bsmtp     unix  -       n       n       -       -       pipe
  flags=Fq. user=bsmtp argv=/usr/lib/bsmtp/bsmtp -t\$nexthop -f\$sender \$recipient
scalemail-backend unix  -       n       n       -       2       pipe
  flags=R user=scalemail argv=/usr/lib/scalemail/bin/scalemail-store \${nexthop} \${user} \${extension}
mailman   unix  -       n       n       -       -       pipe
  flags=FR user=list argv=/usr/lib/mailman/bin/postfix-to-mailman.py
  \${nexthop} \${user}
dovecot   unix  -       n       n       -       -       pipe
  flags=DRhu user=vmail:vmail argv=/usr/lib/dovecot/deliver -d \${recipient}
submission inet n       -       -       -       -       smtpd
  -o smtpd_enforce_tls=yes
  -o smtpd_tls_security_level=encrypt
  -o smtpd_client_restrictions=permit_sasl_authenticated,reject
EOF
#Writing /etc/postfix/mysql_virtual_alias_maps.cf
cat > mysql_virtual_alias_maps.cf <<EOF
hosts = localhost
user = postfix
password = MYSQLPW
dbname = postfixdb
query = SELECT goto FROM alias WHERE address='%s' AND active = '1'
EOF
#Writing /etc/postfix/mysql_virtual_mailbox_maps.cf
cat > mysql_virtual_mailbox_maps.cf <<EOF
hosts = localhost
user = postfix
password = MYSQLPW
dbname = postfixdb
query = SELECT maildir FROM mailbox WHERE username='%s' AND active = '1'
EOF
#Writing /etc/postfix/mysql_sender_login_maps.cf
cat > mysql_sender_login_maps.cf <<EOF
hosts = localhost
user = postfix
password = MYSQLPW
dbname = postfixdb
query = SELECT username AS allowedUser FROM mailbox WHERE username="%s" AND active = 1 UNION SELECT goto FROM alias WHERE address="%s" AND active = 1
EOF
#Writing /etc/postfix/mysql_virtual_domains_maps.cf
cat > mysql_virtual_domains_maps.cf <<EOF
hosts = localhost
user = postfix
password = MYSQLPW
dbname = postfixdb
query = SELECT domain FROM domain WHERE domain='%s' AND active = '1'
EOF
#change rights
cd /etc/postfix
chmod o-rwx,g+r mysql_*
chgrp postfix mysql_*
mv /etc/dovecot/dovecot.conf /etc/dovecot/dovecot.conf.sample
cat > /etc/dovecot/dovecot.conf <<EOF
auth_mechanisms = plain login
log_timestamp = "%Y-%m-%d %H:%M:%S "
passdb {
  args = /etc/dovecot/dovecot-mysql.conf
  driver = sql
}
namespace inbox {
  inbox = yes
  location =
  separator = .
  prefix =
  mailbox Drafts {
    auto = subscribe
    special_use = \Drafts
  }
  mailbox Sent {
    auto = subscribe
    special_use = \Sent
  }
  mailbox Trash {
    auto = subscribe
    special_use = \Trash
  }
  mailbox Junk {
    auto = subscribe
    special_use = \Junk
  }
}
protocols = imap pop3
service auth {
  unix_listener /var/spool/postfix/private/auth_dovecot {
    group = postfix
    mode = 0660
    user = postfix
  }
  unix_listener auth-master {
    mode = 0600
    user = vmail
  }
  user = root
}
listen = *
ssl_cert = </etc/postfix/sslcert/mailserver.crt
ssl_key = </etc/postfix/sslcert/mailserver.key
ssl_protocols = !SSLv3 !SSLv2
ssl_cipher_list = EDH+CAMELLIA:EDH+aRSA:EECDH+aRSA+AESGCM:EECDH+aRSA+SHA384:EECDH+aRSA+SHA256:EECDH:+CAMELLIA256:+AES256:+CAMELLIA128:+AES128:+SSLv3:!aNULL:!eNULL:!LOW:!3DES:!MD5:!EXP:!PSK:!DSS:!RC4:!SEED:!ECDSA:CAMELLIA256-SHA:AES256-SHA:CAMELLIA128-SHA:AES128-SHA
userdb {
  args = /etc/dovecot/dovecot-mysql.conf
  driver = sql
}
protocol pop3 {
  pop3_uidl_format = %08Xu%08Xv
}
protocol lda {
  auth_socket_path = /var/run/dovecot/auth-master
  postmaster_address = postmaster@mailserver.com
}
EOF
#writing /etc/dovecot/dovecot-mysql.conf
cat > /etc/dovecot/dovecot-mysql.conf <<EOF
driver = mysql
connect = "host=localhost dbname=postfixdb user=postfix password=MYSQLPW"
default_pass_scheme = MD5-CRYPT
password_query = SELECT password FROM mailbox WHERE username = '%u'
user_query = SELECT CONCAT('maildir:/var/vmail/',maildir) AS mail, 5000 AS uid, 5000 AS gid FROM mailbox INNER JOIN domain WHERE username = '%u' AND mailbox.active = '1' AND domain.active = '1'
EOF
chmod o-rwx,g+r /etc/dovecot/dovecot-mysql.conf
chgrp vmail /etc/dovecot/dovecot-mysql.conf
/etc/init.d/postfix restart
/etc/init.d/dovecot restart
/etc/init.d/apache2 restart

#postfix configuration
mv /var/www/postfixadmin /var/www/html/
curl http://127.0.0.1/postfixadmin/setup.php
curl -d "form=createadmin&setup_password=PWfMS2015&username=postmaster@mailserver.com&password=PWfMS2015&password2=PWfMS2015&submit=Add+Admin"  http://127.0.0.1/postfixadmin/setup.php

#setup mailing domain and users
#every possible user gets an own user
source /tmp/mailsetup/genDomain.sh mailserver.example
subnet=0
host=0
while [ $subnet -le 255 ]
do
	while [ $host -le 255 ]
	do
		user=`printf "user.%03d.%03d" $subnet $host`
		sh /tmp/mailsetup/genUser.sh $user mailserver.example
		host=$((host+1))
	done
	subnet=$((subnet+1))
	host=0
done

# Configure auto login 
cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf <<EOF
[Service]
ExecStart=
ExecStart=-/sbin/agetty --autologin debian --noclear %I 38400 linux
EOF

# Necessary for finding the NetBIOS name 
#samba
echo "Looking for package samba."
if dpkg -s samba | grep -q Status; then
    echo "samba found."
else
    echo "samba not found. Setting up samba..."
    apt-get --force-yes --yes install samba
fi

# Cron daemon set up to make every night at 01:00 clock updates
echo -e "0 1 * * * sudo bash -c 'apt-get update && apt-get upgrade' >> /var/log/apt/myupdates.log" >> mycron

# Mount the mount point for backup
mkdir /home/debian/backup/

# Download the script to set up the backup server
wget -O /home/debian/backup.py YOUR_SERVER_IP/scripts/requirements/server/mail/backup.py

# Run the script to set up the backup server on a regular basis
echo -e "55 21 * * * sudo bash -c 'python /home/debian/backup.py'" >> mycron

# Run backup service periodically
echo -e "0 22 * * * sudo bash -c 'tar -cf /home/debian/backup/backup.tar /var/vmail/'\n" >> mycron

crontab mycron
rm mycron

# User for ssh script 
useradd -m -s /bin/bash stack
echo "stack:YOUR_PASSWORD" | chpasswd
usermod -a -G sudo stack

# Prettify Prompt 
echo -e "PS1='\[\033[1;37m\]\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\u@\h:\[\033[41;37m\]\w\$\[\033[0m\] '" >> /home/debian/.bashrc

reboot
