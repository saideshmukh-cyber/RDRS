install:
	python -m pip install -r requirements.txt
run:
	python -m app.main
test:
	pytest -q
coverage:
	pytest --cov=app --cov-report=term-missing
