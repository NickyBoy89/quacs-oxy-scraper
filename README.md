# Info

This project is a repository for all the scrapers that integrate the data from Occidental College (OXY) into much more managable and formattable `json` files that then can easily integrated into a course scheduling software named [Quacs](https://github.com/quacs/quacs)

# Requirements

1. Python 3
1. The python pachages `requests bs4 lxml tqdm json`

# How the data comes together

1. There are several separate scraping scripts, each with a different function
    1. `sis_scraper` takes into account the actual courses, and returns `courses.json` and `mod.rs`
    1. `catalog_scraper` takes the course catalog and returns `catalog.json`
    1. `rmp_scraper` gets professor ratings from [RateMyProfessors](https://ratemyprofessors.com) and returns `rmp.json`
    1. `prerequisite_scraper` finds prerequisites for courses and returns `prerequisites.json`
    1. `faculty_directory_scraper` scans the faculty directory and returns `faculty.json`

# Running the Script

1. Every scraper has its individual folder, in the section `How the data comes together`
1. Navigate into the respective folder and run the `main.py` function by typing `python3 main.py`

NOTE: Please note that some of the functions may take longer than thirty seconds to run
