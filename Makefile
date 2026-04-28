.PHONY: plot clean test

all:
	@echo There is no default make target.

plot:
	uv run make-plot

clean:
	rm -rf \
               __pycache__ \
               .pytest_cache \
               src/**/__pycache__ \
               test/__pycache__ \
               *.egg-info \
               src/*.egg-info \
               dist \
               build
	find . \( -name "*.pyo" -o -name '*~' \) -delete

test:
	uv run pytest test/ -v
