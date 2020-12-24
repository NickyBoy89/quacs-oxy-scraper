all: semesterdata catalog faculty prerequisites rmp sis

clean:
	find . -name '*.json' -delete
	rm sis_scraper/mod.rs

catalog:
	cd catalog_scraper && python3 main.py

faculty:
	cd faculty_directory_scraper && python3 main.py

prerequisites:
	cd prerequisite_scraper && python3 main.py

rmp:
	cd rmp_scraper && python3 main.py

sis:
	cp catalog_scraper/catalog.json sis_scraper
	cd sis_scraper && python3 main.py

semesterdata:
	cd semesters && python3 main.py
	cp semesters/semesters.json catalog_scraper
	cp semesters/semesters.json prerequisite_scraper
	cp semesters/semesters.json rmp_scraper
	cp semesters/semesters.json sis_scraper
