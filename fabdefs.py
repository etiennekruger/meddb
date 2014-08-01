from fabric.api import env


def production():
    """
    Env parameters for the production environment.
    """

    env.host_string = '83.143.26.51'
    env.user = 'ubuntu'
    env.project_dir = '/var/www/med-db'
    env.config_dir = 'config/production'
    env.activate = 'source %s/env/bin/activate' % env.project_dir
    print("PRODUCTION ENVIRONMENT\n")
    return


def staging():
    """
    Env parameters for the staging environment.
    """

    env.host_string = 'ubuntu@54.191.89.39'
    env.key_filename = '~/.ssh/code4sa-petrus.pem'
    env.project_dir = '/var/www/med-db'
    env.config_dir = 'config/staging'
    env.activate = 'source %s/env/bin/activate' % env.project_dir
    print("STAGING ENVIRONMENT\n")
    return