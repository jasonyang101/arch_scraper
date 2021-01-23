# arch_scraper
Basic premise:
- execute_scraping is the file to run
Run script as such: (all will run all 3)
- python3 execute_scraping all
- python3 execute_scraping indeed
- python3 execute_scraping indeed dentalpost
- python3 execute_scraping dentalpost ihire

Output will go to the results folder, and be named output.csv, stats.txt, and failed_searches.txt.
If you decide to re-run the script, then the existing above files will be DELETED and re-created. If you want to save it, do a save-as and rename it.

Output.csv:
- These are the csv headers: 'company_name', 'role', 'address', 'city state', 'zip', 'source website'
- under zip, some of them may say 'missing zip'. That means that the google api didn't give a well formatted address.
- There should be *very* few of these, if there are, I'd manually fix them
- Under the role, if multiple of the same location showed up for multiple job searches, then we'd combine the role with a '+' sign.

Failed Searches:
- Shows the places that the we were unable to find a google search response for.

Stats.txt
- Shows how many entries + how many per role
- each number per role won't add up to the total, in case one place has multiple roles in the search output
