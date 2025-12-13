# Week 3 Activity 4 – SQLite OOP Demo

This folder holds my Week 3 Activity 4 submission. The assignment asks for an object-oriented Python project that uses SQLite3, recreates the designed database from Week 3 Activity 3, and prints two answers:

1. How many students are enrolled in course `MSE800`.
2. Which teachers are teaching course `MSE801`.

## File overview
- `activity4.py` – main script. It creates the schema, seeds demo data, and prints the two required outputs.
- `college_db.py` – helper class that handles every SQL command (create tables, insert, and reports).
- `student.py`, `teacher.py`, `course.py` – simple classes that store the data for each entity and know how to save themselves via `CollegeDB`.

## How to run it
1. Make sure Python 3 is installed (any standard installation will work because the only dependency is `sqlite3`, which ships with Python).
2. From this folder run:
   ```bash
   python3 activity4.py
   ```
3. The script will recreate `college.db`, seed sample data, and print something like:
   ```
   Number of students in MSE800: 4
   Teachers teaching MSE801:
   - Amy Wilson
   - John Smith
   ```
