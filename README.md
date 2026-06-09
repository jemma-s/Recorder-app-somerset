# E1000 Recorder App - Somerset Masters Swimming Club

A desktop app built with PyQt6 to streamline the processes associated with being the recorder at Somerset Masters Swimming Club. The app allows the recorder to obtain real-time swim meet and endurance results. 

![Demo](/assets/demos/Demo-E1000-download-0906.gif)

## Purpose
To create a user-friendly interface for the Somerset recorder to web scrape data from the Masters Swimming Australia website without needing prior coding knowledge. 

Before the app was developed, the recorder used to manually enter all endurance (E1000) results into an Excel spreadsheet. 

Swim meet results were also manually searched and points were added up annually to prepare for the year-end awards. 

Both of these tasks were time-intensive processes. Previously, the committee had many members who were retired or happy to spend time completing manual tasks. However, the club is in a transitional period with a higher percentage of younger members. These members do not have the same capacity to continue these manual processes. 

This meant manual processes like updating the E1000 spreadsheet was being neglected and quickly became a bottleneck in displaying up-to-date results.

## Data source
To use most tabs in the app, the recorder will use a file obtained from SwimCentral. This is a website that manages swimming memberships. 

For privacy reasons, these files are not stored on GitHub. However, a [demonstration file](https://github.com/jemma-s/Recorder-app-somerset/blob/main/assets/example-member%20report.csv) containing only my details has been created for the purpose of testing the app. 

Endurance results are sourced from the [Endurance 1000 Portal](https://e1000.msarc.org.au/results/results.php)

Swim meet results are sourced from the [Masters Swimming Australia Portal](https://portal.msarc.org.au/results/results.php?js=on)

## How to use
Run the app.py file. 

## Processes
### Somerset endurance results
![Demo](/assets/demos/Demo-E1000-download-0906.gif)
Purpose:
To obtain the current endurance results from the [Endurance 1000 Portal](https://e1000.msarc.org.au/results/results.php) of the Somerset Masters members. 

How to use:
* Upload the members data csv in the 'Upload Members' tab.
* Once uploaded, you can see a list of members which have been imported.
* Click on the 'E1000 Results' tab.
* Select the desired year. It will default to 2026.
* Click the button to start the web scraper.
* A display will show up to show the progress of the scraper.
* Once done, a pop-up will appear.
* You can then see a list of results which have been obtained.
* To save the results, click the download button. 

### Somerset meet results
![Demo](/assets/demos/Demo-meet-download-0906.gif)
Purpose: 
To get swim meets results from the [Masters Swimming Australia Portal](https://portal.msarc.org.au/results/results.php?js=on) of the Somerset Masters members. 

How to use:
* Upload the members data csv in the 'Upload Members' tab.
* Once uploaded, you can see a list of members which have been imported.
* Click on the 'Swim Meets Results' tab.
* Select the desired year. It will default to 2026.
* Click the button to obtain a list of completed swim meets from the selected year.
* A list of result options will come up. Select the one which is relevant for your purpose.
* If 'Results of a certain swimmer for the year' or 'Results of a certain meet' are selected, you will be prompted to select a swimmer or swim meet.
* Click the button to scrape the swim meet results.
* Once completed, you can then see a list of results which have been obtained.
* To save the results, click the download button. 

### Other club endurance results
![Demo](/assets/demos/Demo-E1000-other-club-download-0906.gif)
Purpose:
To obtain the current endurance results from the [Endurance 1000 Portal](https://e1000.msarc.org.au/results/results.php) of a masters swimming club. If you don't have a list of members, you can use this method as it scrapes a list of masters members from a selected swimming club. This is not the preferred option for Somerset Masters as the source of swimmers from each club is only updated on a monthly basis. 

How to use:
* Select the desired year in the 'Other club members' tab. It will default to 2026.
* Click the button to scrape the available clubs.
* Click the desired club code.
* A table of swimmers will be displayed to sense-check the results.
* Click the 'Other club E1000 Results' tab.
* Select the desired year. It will default to 2026.
* Click the button to start the web scraper.
* A display will show up to show the progress of the scraper.
* Once done, a pop-up will appear.
* You can then see a list of results which have been obtained.
* To save the results, click the download button. 

## Future improvements
* Improved error handling and pop up notifications.
* Contain the app and distribute to other committee members to obtain feedback. 



