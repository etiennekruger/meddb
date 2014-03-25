from __future__ import with_statement
import sys
from fabric.api import *
from contextlib import contextmanager

try:
    from fabdefs import *
except ImportError:
    print "Ensure that you have a fabdefs.py in your directory. Copy fabdefs.py.example and use that as a template"
    sys.exit(1)


@contextmanager
def virtualenv():
    with cd(env.project_dir):
        with prefix(env.activate):
            yield


def upload_db():
    put('med-db.db', '/tmp/med-db.db')
    sudo('mv /tmp/med-db.db %s/med-db.db' % env.project_dir)
    set_permissions()
    restart()
    return


def restart():
    sudo("supervisorctl restart frontend")
    sudo("supervisorctl restart med-db")
    sudo('service nginx restart')
    return


def set_permissions():
    """
     Ensure that www-data has access to the application folder
    """

    sudo('chown -R www-data:www-data ' + env.project_dir)
    return


def setup():

    # install packages
    sudo('apt-get install build-essential')
    sudo('apt-get install python-pip supervisor')
    sudo('pip install virtualenv')

    # create application directory if it doesn't exist yet
    with settings(warn_only=True):
        if run("test -d %s" % env.project_dir).failed:
            # create project folder
            sudo("touch %s" % env.project_dir)
        if run("test -d %s/env" % env.project_dir).failed:
            # create virtualenv
            sudo('virtualenv --no-site-packages %s/env' % env.project_dir)

    # install the necessary Python packages
    with virtualenv():
        put('requirements.txt', '/tmp/requirements.txt')
        sudo('pip install -r requirements.txt')

    # install nginx
    sudo('apt-get install nginx')
    # restart nginx after reboot
    sudo('update-rc.d nginx defaults')
    sudo('service nginx start')
    return


def configure():
    """
    Configure Nginx, supervisor & Flask. Then restart.
    """

    with settings(warn_only=True):
        # disable default site
        sudo('rm /etc/nginx/sites-enabled/default')

    # upload nginx server blocks
    put(env.config_dir + '/nginx.conf', '/tmp/nginx.conf')
    sudo('mv /tmp/nginx.conf %s/nginx_med-db.conf' % env.project_dir)

    # link server blocks to Nginx config
    with settings(warn_only=True):
        sudo('ln -s %s/nginx_med-db.conf /etc/nginx/conf.d/' % env.project_dir)

    # upload supervisor config
    put(env.config_dir + '/supervisor.conf', '/tmp/supervisor.conf')
    sudo('mv /tmp/supervisor.conf /etc/supervisor/conf.d/supervisor_pmgbilltracker.conf')
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

    # configure Flask
    with settings(warn_only=True):
        sudo('mkdir %s/instance' % env.project_dir)
    put(env.config_dir + '/config.py', '/tmp/config.py')
    put(env.config_dir + '/config_private.py', '/tmp/config_private.py')
    sudo('mv /tmp/config.py ' + env.project_dir + '/instance/config.py')
    sudo('mv /tmp/config_private.py ' + env.project_dir + '/instance/config_private.py')

    restart()
    return


def deploy():
    # create a tarball of our packages
    local('tar -czf med-db.tar.gz med-db/', capture=False)
    local('tar -czf frontend.tar.gz frontend/', capture=False)

    # upload the source tarballs to the server
    put('med-db.tar.gz', '/tmp/med-db.tar.gz')
    put('frontend.tar.gz', '/tmp/frontend.tar.gz')

    with settings(warn_only=True):
        sudo('service nginx stop')

    # enter application directory
    with cd(env.project_dir):
        # and unzip new files
        sudo('tar xzf /tmp/med-db.tar.gz')
        sudo('tar xzf /tmp/frontend.tar.gz')

    # now that all is set up, delete the tarballs again
    sudo('rm /tmp/med-db.tar.gz')
    sudo('rm /tmp/frontend.tar.gz')
    local('rm med-db.tar.gz')
    local('rm frontend.tar.gz')

    set_permissions()
    restart()
    return
