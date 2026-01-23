# Week 5 - Activity 6 - Encapsulation

## What the code shows
- `Person` uses a protected attribute `_name`, which is accessible in subclasses.
- `PersonPrivate` uses a private attribute `__name`, which is name-mangled and not directly accessible in subclasses.

## Expected results
- In the protected case, both `Student.greet()` and `Person.greet()` can read `_name`, so the output is similar (same name, different greeting text).
- In the private case, `StudentPrivate.greet()` cannot access `__name` and triggers an `AttributeError`, while `PersonPrivate.greet()` and `get_name()` still work.

## Run
```
python3 PSD/Week05/activity6/student.py
```
