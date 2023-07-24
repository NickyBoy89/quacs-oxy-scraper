.PHONY: all
all: semesterdata catalog faculty prerequisites rmp sis

.PHONY: clean
clean:
	find . -name '*.json' -delete
	rm sis_scraper/mod.rs

.PHONY: catalog
catalog: semesterdata
	cp semesters/semesters.json catalog_scraper
	cd catalog_scraper && python3 main.py

.PHONY: faculty
faculty:
	cd faculty_directory_scraper && python3 main.py

.PHONY: prerequisites
prerequisites:
	cp semesters/semesters.json prerequisite_scraper
	cd prerequisite_scraper && python3 main.py

.PHONY: rmp
rmp:
	cp semesters/semesters.json rmp_scraper
	cd rmp_scraper && python3 main.py

.PHONY: sis
sis:
	cp semesters/semesters.json sis_scraper
	cp catalog_scraper/catalog.json sis_scraper
	cd sis_scraper && python3 main.py

.PHONY: schools
schools:
	cp semesters/semesters.json school_scraper
	cd school_scraper && python3 main.py

.PHONY: semesterdata
semesterdata:
	cd semesters && python3 main.py
