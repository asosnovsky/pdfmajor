
install-development:
	python3 -m venv venv
	./venv/bin/pip install -e .[dev]

clean:
	rm -rf venv
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info

lint:
	black pdfmajor
	bandit -r pdfmajor
	mypy pdfmajor

test:
	./venv/bin/python -m unittest discover tests 

build-docs:
	mkdocs build

deploy:
	python setup.py sdist bdist_wheel
	git tag $(cat .version)
	git push -u origin $(cat .version)
	twine upload dist/*
