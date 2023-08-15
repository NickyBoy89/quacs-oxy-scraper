PY=python3

.PHONY: all
all: semesters.json catalog faculty prerequisites sis

semesters.json: semesters.py
	$(PY) semesters.py

catalog.json: semesters.json catalog_scraper.py
	$(PY) catalog_scraper.py

prerequisites.json: semesters.json prerequisite_scraper.py
	$(PY) prerequisite_scraper.py

sis.json: semesters.json catalog.json sis_scraper.py
	$(PY) sis_scraper.py

schools.json: semesters.json school_scraper.py
	$(PY) school_scraper.py

faculty.json: faculty_directory_scraper.py
	$(PY) faculty_directory_scraper.py

.PHONY: test
test:
	$(PY) -m unittest -v --failfast prerequisite_parser

.PHONY: clean
clean:
	find . -name '*.json' -delete
	rm mod.rs
