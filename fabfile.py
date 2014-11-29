from __future__ import with_statement
import sys
from fabric.api import *
from contextlib import contextmanager
from fabric.contrib.console import confirm
import os
# import backend
import requests

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


def upgrade_db():
    with virtualenv():
        with cd(env.project_dir):
            sudo('alembic upgrade head')
    return


def downgrade_db():
    with virtualenv():
        with cd(env.project_dir):
            sudo('alembic downgrade -1')
    return


def upload_db_backup():
    # compress the sql dump
    local('tar -czf /tmp/med_db.sql.tar.gz /tmp/med_db.sql', capture=False)
    # upload to the server
    put('/tmp/med_db.sql.tar.gz', '/tmp/med_db.sql.tar.gz')
    # and unzip new files
    with cd("/tmp"):
        # remove existing dump, if neccessary
        with settings(warn_only=True):
            sudo('rm -f /tmp/med_db.sql')
        run('tar xzf /tmp/med_db.sql.tar.gz')
        # now, move it out of the dir that it was zipped with
        run('mv /tmp/tmp/med_db.sql /tmp/med_db.sql')
        sudo('rm -R /tmp/tmp')
    # and delete the zip files
    sudo('rm -f /tmp/med_db.sql.tar.gz')
    local('rm -f /tmp/med_db.sql.tar.gz')
    return


def download_db_backup():
    # compress the database dump
    run('tar -czf /tmp/med_db.sql.tar.gz /tmp/med_db.sql')
    # download the zip
    tmp = get('/tmp/med_db.sql.tar.gz', '/tmp/med_db.sql.tar.gz')
    if tmp.succeeded:
        print "Success"
    # now unzip and cleanup manually
    return

def s3_setup_backup():
    print "Ensure that you have edited config/production/s3cfg to your environment"
    sudo('apt-get -y -qq install s3cmd')
    put('config/production/s3cfg', '.s3cfg')
    put('scripts/db-s3-backup.sh', '')
    run('chmod u+x db-s3-backup.sh', 'db-s3-backup.sh')

def s3_db_backup():
    sudo('./db-s3-backup.sh')

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


def setup_auto_security_updates():
    sudo('apt-get -y -qq install unattended-upgrades')
    sudo('sudo dpkg-reconfigure -plow unattended-upgrades')

def setup():

    sudo('apt-get -qq update')

    # install packages
    sudo('apt-get -y -qq install build-essential python-dev sqlite3 libsqlite3-dev')
    sudo('apt-get -y -qq install python-pip supervisor git')
    sudo('apt-get -y -qq install postgresql postgresql-contrib libpq-dev')
    sudo('pip install -q virtualenv')
    sudo('/etc/init.d/supervisor restart')
    sudo('/etc/init.d/postgresql restart')

    setup_auto_security_updates()

    # create application directory if it doesn't exist yet
    with settings(warn_only=True):
        if run("test -d %s" % env.project_dir).failed:
            # create project folder
            sudo("mkdir -p %s" % env.project_dir)
        if run("test -d %s/env" % env.project_dir).failed:
            # create virtualenv
            sudo('virtualenv --no-site-packages %s/env' % env.project_dir)

    # install the necessary Python packages
    with virtualenv():
        put('requirements.txt', '/tmp/requirements.txt')
        sudo('pip install -q -r /tmp/requirements.txt')

    # install nginx
    sudo('apt-get -y -qq install nginx')
    # restart nginx after reboot
    sudo('update-rc.d nginx defaults')
    with settings(warn_only=True):
        sudo('service nginx start')

    setup_database()

def setup_database():
    db_exists = sudo('psql -lqt | cut -d \| -f 1 | grep -w med_db | wc -l', user='postgres') == '1'
    if not db_exists:
        put('scripts/postgres_encoding_correction.sql', '/tmp/postgres_encoding_correction.sql')
        sudo('psql < /tmp/postgres_encoding_correction.sql', user='postgres')
        sudo('createuser med_db --pwprompt', user='postgres')
        sudo('createdb -O med_db med_db', user='postgres')
        if os.path.exists('/tmp/med_db.sql'):
            put('db.dump', '/tmp/med_db.sql')
            sudo('psql med_db < /tmp/med_db.sql', user='postgres')

def configure():
    """
    Configure Nginx, supervisor & Flask. Then restart.
    """

    with settings(warn_only=True):
        # disable default site
        sudo('rm -f /etc/nginx/sites-enabled/default')

    # upload nginx server blocks
    put(env.config_dir + '/nginx.conf', '/tmp/nginx.conf')
    sudo('mv /tmp/nginx.conf /etc/nginx/sites-available/med-db.medicines.sadc.int')

    # link server blocks to Nginx config
    with settings(warn_only=True):
        sudo('rm -f /etc/nginx/sites-enabled/med-db.medicines.sadc.int')
        sudo('ln -s /etc/nginx/sites-available/med-db.medicines.sadc.int /etc/nginx/sites-enabled/')

    # upload supervisor config
    put(env.config_dir + '/supervisor.conf', '/tmp/supervisor.conf')
    sudo('mv /tmp/supervisor.conf /etc/supervisor/conf.d/supervisor_med-db.conf')
    sudo('supervisorctl reread')
    sudo('supervisorctl update')

    # configure Flask and virtualenv
    with settings(warn_only=True):
        sudo('mkdir -p %s/instance' % env.project_dir)
    put(env.config_dir + '/config.py', '/tmp/config.py')
    put(env.config_dir + '/config_private.py', '/tmp/config_private.py')
    sudo('mv /tmp/config.py ' + env.project_dir + '/instance/config.py')
    sudo('mv /tmp/config_private.py ' + env.project_dir + '/instance/config_private.py')

    # configure newrelic
    try:
        put(env.config_dir + '/newrelic.ini', '/tmp/newrelic.ini')
        sudo('mv /tmp/newrelic.ini /var/www/med-db/newrelic.ini')
    except ValueError:
        # not all environment configs will have a newrelic.ini file present
        pass

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
        # delete existing debug log, if present
        with settings(warn_only=True):
            sudo('rm -f debug.log')

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
    sudo('apt-get -y -qq install tcl8.5')
    sudo('apt-get -y -qq install wget')
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
                sudo('mkdir -p /etc/redis')
                sudo('mkdir -p /var/redis')
                sudo('touch /var/log/redis_6379.log')
            # init file for handling server restart
            sudo('cp utils/redis_init_script /etc/init.d/redis_6379')
            # copy config file
            sudo('cp redis.conf /etc/redis/6379.conf')
            with settings(warn_only=True):
                # create working directory
                sudo('mkdir -p /var/redis/6379')

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

available_countries = {
    "AGO":  "Angola",
    "BWA":  "Botswana",
    "COD":  "Congo (DRC)",
    "LSO":  "Lesotho",
    "MWI":  "Malawi",
    "MUS":  "Mauritius",
    "MOZ":  "Mozambique",
    "NAM":  "Namibia",
    "SYC":  "Seychelles",
    "ZAF":  "South Africa",
    "SWZ":  "Swaziland",
    "TZA":  "Tanzania",
    "ZMB":  "Zambia",
    }

def seed_production_cache():

    # list of endpoints to hit
    endpoints = [
        "",
        "country-ranking/",
    ]

    for code, name in available_countries.iteritems():
        endpoints.append("country-report/" + code + "/")

    # hit each endpoint
    for endpoint in endpoints:
        url = "http://med-db.medicines.sadc.int/" + endpoint
        print "hitting " + url
        response = requests.get(url)
    return


def flush_redis():

    sudo('redis-cli flushdb')
    seed_production_cache()
    return
