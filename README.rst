===========================
Running Records Application
===========================

Description
===========

This program provides a graphical user interface for the management of running records,
and show of weekly running distance and weekly average speed.

Author
======
Angelo Varlotta, 2022

Features
========

* Provides a validated entry form to ensure correct data,
* Allows update / removal of record information,
* Allows sorting by date, distance, pace, speed and location,
* Shows bar chart of weekly cumulative distance achievement,
* Shows bar chart of weekly average speed achievement,
* Shows bar chart of of number of weekly running sessions,
* Allows bar chart views over the previous 1, 3, 6 and 9 month spans,
* Import and export of data in CSV formats,
* Creates stacked bar chart for marathon training programs. Requires CSV file with runs for each day of the week.

Requirements
============

* Python (>=3.8.x),
* Tkinter (normally part of the built-in packages in Python, however if installing Python 3.9.x and above with Homebrew you may need to install it separately ('brew install python-tk@3.9')),
* SQLite (>= 3.37.2), install with 'python -m pip install sqlite',
* matplotlib (>=3.5.x), install with 'python -m pip install matplotlib'.

Notes
=====

* Import of CSV data needs columns containing Date, Duration, Distance, Pace, Speed and Location,
* Export feature will extract to a CSV file in a likewise column fashion,
* Marathon program import takes name from file basename (name without extension), import will fail if the program has already been imported.

Issues
======

* Draw feature of bar chart plots can be slow for higher look-back periods for 6 months on over.
