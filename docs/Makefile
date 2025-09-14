# Simple doc build wrapper using antsibull-docs + sphinx

.PHONY: help prepare html clean

DOCSITE_DIR := docs/docsite
BUILD_DIR := docs/_build/html

help:
	@echo "make prepare  # generate Sphinx sources with antsibull-docs"
	@echo "make html     # build HTML docs with sphinx-build"
	@echo "make clean    # remove generated sources and build outputs"

prepare:
	antsibull-docs collection docsite \
	  --use-current \
	  --squash-hierarchy \
	  --dest-dir $(DOCSITE_DIR)

html: prepare
	sphinx-build -b html $(DOCSITE_DIR) $(BUILD_DIR)

clean:
	rm -rf $(DOCSITE_DIR) docs/_build

