# YaTube
## _The Last Social network, Ever_

Through this project, users will be able to:

- Create an account
- Publish posts
- Subscribe to favorite authors
- Tag posts they like

## Tech

YaTube uses a number of open source projects to work properly:

- [Python 3.7] - Python is powerful.
- [Django 2.2.19] - The web framework for perfectionists with deadlines.

And of course YaTube itself is open source with a [public repository][git-repo-url]
 on GitHub.

## Running a project in dev mode

Install and activate the virtual environment

```sh
cd yatube_project
python -m venv venv
source venv/bin/activate
```

Install the dependencies

```sh
pip install -r requirements.txt
```

Start the server

```sh
cd yatube_project/yatube
python3 manage.py runserver
```

Open [http://127.0.0.1:8000/][dev-server]

## Author
Mikhail Bulankin

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)

   [git-repo-url]: <https://github.com/mvlbulankin/yatube_project.git>
   [Django 2.2.19]: <https://www.djangoproject.com/>
   [Python 3.7]: <https://www.python.org/>
   [dev-server]: <http://127.0.0.1:8000/>
