all: semesterdata catalog faculty prerequisites rmp sis

catalog:
	cd catalog_scraper && python3 main.py

faculty:
	cd faculty_directory_scraper && python3 main.py

prerequisites:
	cd prerequisite_scraper && python3 main.py

rmp:
	cd rmp_scraper && python3 main.py

sis:
	cd sis_scraper && python3 main.py

semesterdata:
	cd semesters && python3 main.py
