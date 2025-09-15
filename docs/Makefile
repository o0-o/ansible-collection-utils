# Simple doc build wrapper using antsibull-docs + sphinx

.PHONY: help prepare html clean

DOCSITE_DIR := docsite
BUILD_DIR := _build/html

help:
	@echo "make prepare  # generate Sphinx sources with antsibull-docs"
	@echo "make html     # build HTML docs with sphinx-build"
	@echo "make clean    # remove generated sources and build outputs"

prepare:
	mkdir -p $(DOCSITE_DIR)
	antsibull-docs sphinx-init \
	  --use-current \
	  --squash-hierarchy \
	  --dest-dir $(DOCSITE_DIR) \
	  o0_o.utils
	antsibull-docs collection \
	  --use-current \
	  --squash-hierarchy \
	  --dest-dir $(DOCSITE_DIR) \
	  o0_o.utils

html: prepare
	sphinx-build -b html $(DOCSITE_DIR) $(BUILD_DIR)

clean:
	rm -rf $(DOCSITE_DIR) _build
