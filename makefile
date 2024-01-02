
.PHONY: pypi help

help:
	@echo " "
	@echo "***************************************************"
	@echo " "
	@echo "This is a makefile to push to pypi."
	@echo "Use make pypi to push to pypi."
	@echo "Note that you may need to bump the version"
	@echo "number in setup.py for pypi to accept a push."
	@echo " "
	@echo "***************************************************"
	@echo " "

pypi: README.rst
	python3 setup.py sdist
	twine upload -r pypi dist/*

README.rst: README.md
	pandoc --from=markdown --to=rst --output=README.rst README.md

