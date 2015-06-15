<VirtualHost *:8080>
    # Accessible by these domain names:
    ServerName marr.cse.buffalo.edu
    ServerAlias supervoxel.com
    ServerAdmin swhitt@buffalo.edu

    #
    # Static documents are served by Apache, for speed
    #
    DocumentRoot /projects/svxlabel/static
    Alias /static /projects/svxlabel/static

    <Directory /projects/svxlabel/static>
        # Far future expires headers for my images
        # ExpiresActive On
        # ExpiresDefault "access plus 1 day"
        # ExpiresByType image/png "access plus 1 year"
        # ExpiresByType image/jpeg "access plus 1 year"

        # No snooping
        # Options -Indexes
    
        Order deny,allow
        Allow from all
    </Directory>

    #
    # Set up mod_wsgi for flask
    #
    WSGIDaemonProcess svxlabel user=www-data group=www-data processes=1 threads=3
    WSGIScriptAlias / /projects/svxlabel/apache_conf/svxlabel.wsgi
    # Reload automatically when svxlabel.wsgi is modified
    WSGIScriptReloading On
    # Allow flask to handle authorization, so flask-basicauth works
    WSGIPassAuthorization On

    <Directory /projects/svxlabel/apache_conf>
        WSGIProcessGroup svxlabel
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>

    #
    # Log to a convenient location
    #
    ErrorLog /projects/svxlabel/logs/error.log
    LogLevel warn
    CustomLog /projects/svxlabel/logs/access.log combined

</VirtualHost>
