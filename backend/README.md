## cd into ./backend

## set up a python venv
> python3 -m venv env

## activate it
windows:
> env/Scripts/activate

linux:
> source env/bin/activate

## update pip
> python3 -m pip install -U pip

## install requirements
> python3 -m pip install -r requirements.txt

## run flask app
> flask run

## if you want auto reloading upon file change
> python3 app.py