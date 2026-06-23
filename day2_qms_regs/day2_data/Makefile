SHELL := /bin/bash -o pipefail -e
.SUFFIXES:
.SECONDARY:
.DELETE_ON_ERROR:

CONFIG := config.yml
DATA_FILES := $(wildcard data/*.yml)
SRC_MDS := $(wildcard docs/**/*.md docs/*.md)
RELEASE_MDS := $(patsubst docs/%.md,release/%.md,$(SRC_MDS))
RELEASE_PDFS := $(patsubst docs/%.md,release/%.pdf,$(SRC_MDS))
RELEASE_DOCS := $(patsubst docs/%.md,release/%.docx,$(SRC_MDS))

all: $(RELEASE_MDS)

pdfs: $(RELEASE_PDFS)

docs: $(RELEASE_DOCS)

release/%.md: docs/%.md $(CONFIG) $(DATA_FILES)
	@mkdir -p $(@D)
	rdm render $< $(CONFIG) $(DATA_FILES) > $@

release/%.pdf: release/%.md pandoc_pdf.yml template.tex
	@mkdir -p $(@D)
	pandoc --defaults=./pandoc_pdf.yml $< -o $@

release/%.docx: release/%.md pandoc_docx.yml
	@mkdir -p $(@D)
	pandoc --defaults=./pandoc_docx.yml $< -o $@

# useful for debugging
release/%.tex: release/%.md pandoc_pdf.yml template.tex
	@mkdir -p $(@D)
	pandoc --defaults=./pandoc_pdf.yml -t latex $< -o $@

# Manually call recipe to pull down your development history
data/history.yml:
	rdm pull $< > $@

.PHONY:
clean:
	rm -rf tmp release
