![Tests](https://github.com/UWmathNEWS/slugline-api/workflows/Tests/badge.svg)
![Python flake8 checks](https://github.com/UWmathNEWS/slugline-api/workflows/Python%20flake8%20checks/badge.svg)
![Python black checks](https://github.com/UWmathNEWS/slugline-api/workflows/Python%20black%20checks/badge.svg)

## slugline-api
The backend portion of `slugline`, math**NEWS**'s best and only Django/React based publishing website.

## Running
- Create a `virtualenv` by running `virtualenv <environment location>`. Python 3.7+ is recommended. Depending on your OS run the following to activate the virtualenv:
	- Windows: `<environment location>/scripts/activate`
	- Linux: `source <environment location>/bin/activate`
- Run `pip install -r requirements.txt` to download dependencies.
- Create a superuser with `./manage.py createsuperuser`. Then run `./manage.py runserver` to start the backend. 
If you want to fiddle with the data, go to `localhost:8000/admin` and login with your superuser credentials.
- By default, this runs on port 8000. If you change this, be sure to go over to the [front-end](http://www.github.com/UWmathNEWS/slugline-web) and change the port setting there.

## Loading data
If you have a XML dump from the math**NEWS** WordPress handy, you can preload the database with it. Just run `./manage.py wordpress <xml_file>` and it'll load in the articles in the dump. However, the articles are not perfect, and should be cleaned up before being made visible to the public.

## Contributing
Submit a pull request or something.
