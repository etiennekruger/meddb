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

    * first comment the following lines in `backend/init.py`

            import admin
            import views

    * now create an empty database

            python
            >>> from backend import models
            >>> from backend import db
            >>> db.create_all()
            >>> db.session.commit()

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


### Maintenance

...

