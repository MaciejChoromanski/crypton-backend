# crypton
Messaging app with end-to-end encryption written with Python 3.

Current progress can be viewed on [Trello](https://trello.com/b/sl5VjPNP/crypton).

## Table of contents
1. [Current stack](#current-stack)
2. [Installation](#installation)
3. [Tests](#tests)
4. [Lint](#lint)
5. [Authors](#authors)
6. [License](#license)

## Current stack
* [Python 3.8](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [Docker](https://www.docker.com/)
* [PostgreSQL](https://www.postgresql.org/)
* [Redis](https://redis.io/)
* [Gunicorn](https://gunicorn.org/)
* [Nginx](https://www.nginx.com/)
* [Flake8](https://flake8.pycqa.org/en/latest/)
* [Pre-commit](https://pre-commit.com/)
* [Travis CI](https://travis-ci.com/)

## Installation
These steps will help you set up the project on your machine. They were written with UNIX/UNIX-like based systems in mind.

### Prerequisites
You'll need [Docker](https://www.docker.com/) and [docker-compose](https://docs.docker.com/compose/) to set up this project properly. You'll also need to create environment files, which will be used by the [Docker](https://www.docker.com/) if you'll like to run this app on a production server.

### Environment preparation (just for production)
You'll need to create env/ directory with .env.prod and .env.db.prod files in order to run.

#### Example of .env.prod file
```
DEBUG=True
SECRET_KEY=key
DJANGO_ALLOWED_HOSTS=0.0.0.0
DB_ENGINE=django.db.backends.postgresql
DB_DATABASE=crypton
DB_USER=postgres
DB_PASSWORD=
DB_HOST=db
DB_PORT=5432
DATABASE=postgres
CACHE_BACKEND=django_redis.cache.RedisCache
CACHE_LOCATION=redis://0.0.0.0:6379/1
CACHE_CLIENT_CLASS=django_redis.client.DefaultClient
CACHE_KEY_PREFIX=key
CACHE_HOST=sess
CACHE_PORT=6379
CACHE=redis
```

#### Example of .env.db.prod file
```
POSTGRES_DB=crypton
POSTGRES_USER=crypton
POSTGRES_PASSWORD=changeme
```

### Installing
The app can be run with [docker-compose](https://docs.docker.com/compose/) or [Makefile](Makefile). The second option is more preferred since it provides all basic instructions (build, up, stop etc.) in a shorter form.

#### Development
Building images:
```
make build
```

Running the app:
```
make run
```

#### Production
Building images:
```
make build_prod
```

Running the app:
```
make run_prod
```

## Tests
Run the tests:
```
make test
```

## Lint
Run the lint:
```
make lint
```

## Authors
* **Maciej Choromański** - *Initial work* - [MaciejChoromanski](https://github.com/MaciejChoromanski)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details