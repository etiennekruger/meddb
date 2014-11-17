med-db
================

SADC Medicines Database: a web application for sharing pharmaceutical procurement information between
countries in the SADC region.


## What does this project do

The SADC Medicines Database brings together data relating to the procurement of medicines from the national
budgets of participating countries. This data is then presented in way that makes it possible to strike
comparisons between the prices paid by the different parties.

This project, including all of its features and content is made available through Southern African Regional
Programme on Access to Medicines and Diagnostics ("SARPAM").


## How it works

The web application can be accessed at http://med-db.medicines.sadc.int/

The database is managed and kept up-to-date through an Admin interface at http://med-db-api.medicines.sadc.int/admin

## Contributing to the project

This project is open-source, and anyone is welcome to contribute. If you just want to make us aware of a bug / make
a feature request, then please add a new GitHub Issue (if a similar one does not already exist).

If you want to contribute to the code, please fork the repository, make your changes, and create a pull request.

### Local setup

* Clone the repository:

        git clone git@github.com:Code4SA/med-db.git

* Create and activate a virtualenv:

        cd med-db
        virtualenv env
        source env/bin/activate

* Install requirements:

        pip install -r 'requirements.txt'

* Update you `hosts` file by adding the following entries:

        127.0.0.1 med-db.medicines.localhost
        127.0.0.1 med-db-api.medicines.localhost

* Initialise an empty database

    * Install PostgreSQL, and run server application. On a Mac:

            brew install postgres
            postgres -D /usr/local/var/postgres

    * Create a new user named `med_db`, with password `med_db` and a database named `med_db`

            createuser med_db --pwprompt
            createdb -O med_db med_db

    * now comment the following lines in `backend/init.py`

            import admin
            import views

    * and create an empty database

            python
            >>> from backend import models, db
            >>> db.create_all()

        and then remember to uncomment those lines from the previous step.

* Run backend server

        python runserver_backend.py

This gives you an api for accessing the data at med-db-api.medicines.localhost, and an admin interface
at med-db-api.medicines.localhost/admin

* Now, open a new terminal, and run the frontend server:

        cd med-db
        source env/bin/activate
        python runserver_frontend.py

    This gives you a frontend, at med-db.medicines.localhost

* To speed up certain view endpoints, you can run a redis instance that will cache the results from computationally
expensive functions. See http://redis.io/topics/quickstart.


### Deploy instructions

To deploy changes to the app, use fabric. For changes to the configuration, simply

    fab production configure

and for changes to the app,

    fab production deploy

If you need the server to install new dependencies, add the to `requirements.txt` and

    fab production setup

To setup Postgres on a new Ubuntu server:

    # install postgres
    sudo apt-get install postgresql postgresql-contrib
    # add a 'postgres' superuser
    sudo passwd postgres
    # as the superuser, create a new user and database for this project
    su - postgres
    createuser med_db --pwprompt
    createdb -O med_db med_db


### Maintenance


Add cronjob for daily db backup::

    su - postgres
    crontab -e
    0 0 * * * pg_dump med_db --no-privileges > /tmp/med_db.sql


To restore the database from a backup::

    su - postgres
    psql med_db < /tmp/med_db.sql


Updating the Babel translation files::

    # compile translations, after updating the translation files
    pybabel compile -d frontend/translations

    # recompile the master translation template, e.g. after changes to the english copy
    cd frontend
    pybabel extract -F babel.cfg -o messages.pot .

    # update translation templates from the master file (keeping existing compiled translations in mind)
    cd ..
    pybabel update -i frontend/messages.pot -d frontend/translations


