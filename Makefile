all: semesterdata catalog faculty prerequisites rmp sis

clean:
	find . -name '*.json' -delete
	rm sis_scraper/mod.rs

catalog:
	cp semesters/semesters.json catalog_scraper
	cd catalog_scraper && python3 main.py

faculty:
	cd faculty_directory_scraper && python3 main.py

prerequisites:
	cp semesters/semesters.json prerequisite_scraper
	cd prerequisite_scraper && python3 main.py

rmp:
	cp semesters/semesters.json rmp_scraper
	cd rmp_scraper && python3 main.py

sis:
	cp semesters/semesters.json sis_scraper
	cp catalog_scraper/catalog.json sis_scraper
	cd sis_scraper && python3 main.py

schools:
	cp semesters/semesters.json school_scraper
	cd school_scraper && python3 main.py

semesterdata:
	cd semesters && python3 main.py
