===========================
Running Records Application
===========================

Description
===========

This program provides a graphical user interface for the management of running records,
and show of weekly running distance and weekly average speed.

Author
======
Angelo Varlotta, 2023

Features
========

* Provides a validated entry form to ensure correct data,
* Allows insertion, update and removal of record information,
* Allows sorting by date, distance, pace, speed and location from header item,
* Shows bar chart for weekly cumulative distance, weekly average speed and number of weekly running sessions,
* Allows bar chart views over the previous 1, 3 and 6 month spans,
* Import and export of data in CSV formats,
* Creates stacked bar chart for marathon training programs,
* Advanced search form that allow search on dates, distances, speeds and paces,
* Summary statistics output in advanced search form in status bar.

Requirements
============

* Python (>=3.8.x),
* Tkinter (normally part of the built-in packages in Python, however if installing Python 3.9.x and above with Homebrew you may need to install it separately ('brew install python-tk@3.9')),
* SQLite (>= 3.37.2), install with 'python -m pip install sqlite',
* matplotlib (>=3.5.x), install with 'python -m pip install matplotlib'.

Notes
=====

* Import of CSV data needs columns containing Date, Duration, Distance, Pace, Speed and Location. Error message box will appear if data contains incorrect columns.
* Export feature will extract to a CSV file in a likewise column fashion.
* Marathon programs import requires CSV file with columns containing all days of the week, in the precise form: Mon, Tue, Wed, Thu, Fri, Sat and Sun.
* Marathon program import takes name from file basename (name without extension), import will fail if the program has already been imported.

Issues
======

* Draw feature of bar chart plots can be slow for higher look-back periods greater than 6 months.
For this reason, lookbacks are limited to 6 months.
* Duration and Pace in advanced search form won't return an error if lower duration and pace are higher than upper duration and pace. Fix is on TODO list.
* When dark mode is set at the OS level the application has white text on a white background, and the TreeView lists are white text on a black field. I've decided to remove dark mode styling and make it maintain its usual visualization mode even when the OS is set for dark mode.
