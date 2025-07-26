# Readme
## Problem Statement
This is a POC based on the following question:<br/>
**Is it possible to create a low-level solution to search CSVs of data on-premise, without having to load them into a database with an ETL task?**

In the cloud, there are a number of other options (EG Athena, Snowflake, ect), but as we are restricting to on-premise, and assuming files in the ranges of a couple of GBs at most, it sounds like a job for Python with Pandas.
If the files are bigger, I would probably look at PySpark or DuckDB.

## Copilot Prompt
As this is also an experiment to create code via with AI assistance, I am using Copilot with the following initial prompt:

Write a script, using python, to create the following:
1) A window for user input, with three fields named "file identifier", "search column", and "search string", and a search button.
2) Find all csv files in a directory (which should be a constant variable to be set in script) that have a name partially matching the file identifier input.
3) Read CSVs and find all rows where the "search column" matches the "search string", and output them as a table.
Code should be scalable to consume roughly 100GB csv files.

## Script Details
### Prerequisites
We will need the following installed

    Python 3.7+
    pandas
    tkinter (bundled with most Python distributions)

### Configuration
Before running the app, set the CSV directory:

    CSV_DIRECTORY = ''  # 🔁 Change this to your actual directory

Additionally, ensure that CSV's to be searched have the same column naming scheme, as we are searching by column.

<br/>

### Sample CSV Requirements
* Must be comma-delimited and have headers<br/>
* Should include the target search column

<br/>

### Error Handling
* Displays alerts for missing input, unreadable files, or columns not found<br/>
* Skips files if column doesn't exist

