# DIYInvestmentPrimer
We want to provide basic and simple info from our investment research

For the development of this app, pipenv was used for the virtual
environment and if you would like to use it then install it by
typing:

`pip install pipenv`


Initial set-up of the app:

on my personal laptop I go to my terminal (I use git bash) to type:

`conda.bat deactivate`

then I create the virtual environment with pipenv by typing in the
terminal. before typing this make sure you're in the root folder of
your application in the terminal:

`pipenv --python 3`

once I have the virtual environment created then I install
the dependencies by typing in the terminal:

`pipenv install Flask Flask-SQLAlchemy Flask-Migrate`

to activate the virtual environment, in your terminal go to the root directory and
simply type:

`pipenv shell`

to run the app locally go to your terminal and in the web_app folder:
# Mac:
`FLASK_APP=web_app flask run`

# Windows:
`export FLASK_APP=web_app` # one-time thing, to set the env var
`flask run`