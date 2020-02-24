# Keck-ADS-API

## Introduction

This repository is built to scrape through the Astrophysics Data System (ADS) to find W.M. Keck Observatory related documents.  The output is a `ADS_exportTObibDB.csv` file containing information on new Keck related documents and `bibcode.txt` of the bibcodes of those documents.

## Installing

```
git clone https://github.com/Terry071896/Keck-ADS-API.git
cd .../Keck-ADS-API
sudo pip install -r requirements.txt
```
This should import all the code and python packages necessary.

### Run from Python

Change directory to the Keck-ADS-API and run
```
python KECK_ADS_API.py
```

### Create Executable Application

Open up terminal/command prompt
```
cd .../Keck-ADS-API
pyinstaller --onefile KECK_ADS_API.py
```

There should be a a couple of new folders created.
If you go to `Keck-ADS-API/dist` the 'dist' folder should contain an executable file that you can double click to run.

## The App Layout

A very basic layout that should show everything in a terminal/command prompt:

The first option
```
Type Search:
```
Enter the search you would regularly do for the search engine at https://ui.adsabs.harvard.edu/.

After words, a maximum of 1000 documents will be search through on that given search (so try and be specific with your searches)

```
100% |########################################################|
100% |########################################################|
Documents added: 56
Documents already there: 244
300 of 326 likely keck related
246 of 326 have keck instrument in text
1. New Search
2. Export
3. Exit WITHOUT Saving
Enter '1', '2', or '3': 
```

The number of documents added are mentioned, with a few statistics shown.
The next input asked allows you to make another search ontop of the previous search (another maximum of 1000 new papers), export the searches and keck related documents to the spreadsheet and text files `ADS_exportTObibDB.csv` and `bibcode.txt`, or exit the app WITHOUT saving/exporting anything searched while the app is running.
