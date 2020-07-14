build:
	docker-compose build

build_prod:
	docker-compose -f docker-compose.prod.yml build

run:
	docker-compose up

run_prod:
	docker-compose -f docker-compose.prod.yml up

test:
	docker-compose run app sh -c "python app/manage.py test"

lint:
	docker-compose run app sh -c "flake8"

logs:
	docker-compose logs -f

stop:
	docker-compose stop

stop_prod:
	docker-compose -f docker-compose.prod.yml stop

down:
	docker-compose down

down_prod:
	docker-compose -f docker-compose.prod.yml down