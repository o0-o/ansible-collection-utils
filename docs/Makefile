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
	  --index-rst-source index.rst \
	  o0_o.utils
	# Append config to exclude generated rst/index.rst from build
	{ \
	  echo "# Added by docs/Makefile to reduce warnings"; \
	  echo "try:"; \
	  echo "    exclude_patterns = list(exclude_patterns)"; \
	  echo "except NameError:"; \
	  echo "    exclude_patterns = []"; \
	  echo "exclude_patterns.append('rst/index.rst')"; \
	} >> $(DOCSITE_DIR)/conf.py
	antsibull-docs collection \
	  --use-current \
	  --squash-hierarchy \
	  --dest-dir $(DOCSITE_DIR) \
	  o0_o.utils

html: prepare
	sphinx-build -b html $(DOCSITE_DIR) $(BUILD_DIR)

clean:
	rm -rf $(DOCSITE_DIR) _build
