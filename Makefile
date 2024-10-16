# running the main.py
run:
	python main.py

run-reloadable:
	uvicorn main:app --reload

# sync dependancies
sync:
	pip install -r "requirements.txt"

# update dependencies
update:
	pip freeze >> requirements.txt

# run migrations
migrate-up:
	python migrate.py up

migrate-down:
	python migrate.py down

migrate-full:
	make migrate-down && make migrate-up