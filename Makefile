# running the main.py
run:
	python main.py

# update dependancies
update:
	pip install -r "requirements.txt"

# run migrations
migrate-up:
	python migrate.py up

migrate-down:
	python migrate.py down	