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

* Provides a validated entry form to ensure correct data
* Allows update / removal of record information
* Allows sorting by date, distance, pace, speed and location
* Shows bar chart of weekly cumulative distance achievement
* Shows bar chart of weekly average speed achievement
* Allows bar chart views over the previous 1, 3, 6, 9 and 12 month spans
* Import and export of data in CSV formats

Requirements
============

* Python (>=3.8.x),
* Tkinter (normally part of the built-in packages in Python, however if installing Python 3.9.x and above with Homebrew you may need to install it separately ('brew install python-tk@3.9')),
* SQLite (>= 3.37.2), install with 'python -m pip install sqlite',
* matplotlib (>=3.5.x), install with 'python -m pip install matplotlib'.

Notes
=====

* Import of CSV data needs columns containing Date, Duration, Distance, Pace, Speed and Location
* Export feature will extract in a likewise column fashion

Issues
======

* Draw feature of bar chart plots can be slow for higher look-back periods over and including 9 months.
