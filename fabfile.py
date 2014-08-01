from __future__ import with_statement
import sys
from fabric.api import *
from contextlib import contextmanager
from fabric.contrib.console import confirm

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
    put('instance/med-db.db', '/tmp/med-db.db')
    sudo('mv /tmp/med-db.db %s/instance/med-db.db' % env.project_dir)
    set_permissions()
    restart()
    return


def restart():
    sudo("supervisorctl restart frontend")
    sudo("supervisorctl restart backend")
    sudo('service nginx restart')
    return


def set_permissions():
    """
     Ensure that www-data has access to the application folder
    """

    sudo('chown -R www-data:www-data ' + env.project_dir)
    return


def setup():

    sudo('apt-get update')

    # install packages
    sudo('apt-get install build-essential python-dev sqlite3 libsqlite3-dev')
    sudo('apt-get install python-pip supervisor')
    sudo('pip install virtualenv')

    # create application directory if it doesn't exist yet
    with settings(warn_only=True):
        if run("test -d %s" % env.project_dir).failed:
            # create project folder
            sudo("mkdir %s" % env.project_dir)
        if run("test -d %s/env" % env.project_dir).failed:
            # create virtualenv
            sudo('virtualenv --no-site-packages %s/env' % env.project_dir)

    # install the necessary Python packages
    with virtualenv():
        put('requirements.txt', '/tmp/requirements.txt')
        sudo('pip install -r /tmp/requirements.txt')

    # install nginx
    sudo('apt-get install nginx')
    # restart nginx after reboot
    sudo('update-rc.d nginx defaults')
    with settings(warn_only=True):
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
    sudo('mv /tmp/nginx.conf /etc/nginx/sites-available/med-db.medicines.sadc.int')

    # link server blocks to Nginx config
    with settings(warn_only=True):
        sudo('ln -s /etc/nginx/sites-available/med-db.medicines.sadc.int /etc/nginx/sites-enabled/')

    # upload supervisor config
    put(env.config_dir + '/supervisor.conf', '/tmp/supervisor.conf')
    sudo('mv /tmp/supervisor.conf /etc/supervisor/conf.d/supervisor_med-db.conf')
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
    local('tar -czf backend.tar.gz backend/', capture=False)
    local('tar -czf frontend.tar.gz frontend/', capture=False)

    # upload the source tarballs to the server
    put('backend.tar.gz', '/tmp/backend.tar.gz')
    put('frontend.tar.gz', '/tmp/frontend.tar.gz')

    with settings(warn_only=True):
        sudo('service nginx stop')

    # enter application directory
    with cd(env.project_dir):
        # and unzip new files
        sudo('tar xzf /tmp/backend.tar.gz')
        sudo('tar xzf /tmp/frontend.tar.gz')

    # now that all is set up, delete the tarballs again
    sudo('rm /tmp/backend.tar.gz')
    sudo('rm /tmp/frontend.tar.gz')
    local('rm backend.tar.gz')
    local('rm frontend.tar.gz')

    set_permissions()
    restart()
    return


def configure_redis():

    # upload config file
    put('instance/redis.conf', '/tmp/redis.conf')
    sudo('mv -f /tmp/redis.conf /etc/redis/6379.conf')

    return


def install_redis():
    """
    Install the redis key-value store on port 6379
    http://redis.io/topics/quickstart
    """
    sudo('apt-get install tcl8.5')
    sudo('apt-get install wget')
    with cd(env.project_dir):
        sudo('wget http://download.redis.io/redis-stable.tar.gz')
        sudo('tar xvzf redis-stable.tar.gz')
        with cd('redis-stable'):
            sudo('make')
            sudo('make test')
            if confirm("Do you want to continue?"):
                #continue processing
                sudo('cp src/redis-server /usr/local/bin/')
                sudo('cp src/redis-cli /usr/local/bin/')
            with settings(warn_only=True):
                # create dir for config files, data and log
                sudo('mkdir /etc/redis')
                sudo('mkdir /var/redis')
                sudo('touch /var/log/redis_6379.log')
            # init file for handling server restart
            sudo('cp utils/redis_init_script /etc/init.d/redis_6379')
            # copy config file
            sudo('cp redis.conf /etc/redis/6379.conf')
            with settings(warn_only=True):
                # create working directory
                sudo('mkdir /var/redis/6379')

            # ensure redis restarts if the server reboots
            sudo('update-rc.d redis_6379 defaults')

    configure_redis()
    # reboot once, to let redis start up automatically
    sudo('reboot')
    return


def test_redis():

    sudo('redis-cli ping')
    return


def restart_redis():

    with settings(warn_only=True):
        sudo('/etc/init.d/redis_6379 stop')
    sudo('/etc/init.d/redis_6379 start')
    return


def flush_redis():
    sudo('redis-cli flushdb')
    return