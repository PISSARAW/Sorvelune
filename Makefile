.PHONY: demo test

demo:
	python3 -m sorvelune examples/simulation.json

test:
	python3 -m unittest discover -s tests -v
