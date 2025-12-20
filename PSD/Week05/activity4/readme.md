# Week 5 - Activity 4: Inheritance

## Project Description
This project demonstrates object-oriented inheritance based on the provided UML structure.

UML structure implemented:
- Person (base class)
  - Student (inherits Person)
  - Staff (inherits Person)
    - General (inherits Staff)
    - Academic (inherits Staff)

## Purpose and Overall Design
- `Person` stores common attributes: id and name.
- `Student` adds student_id.
- `Staff` adds staff_id and tax_num.
- `General` adds rate_of_pay and a pay calculation method.
- `Academic` adds publications and publication management methods.

Run `python3 main.py` to see inheritance + method overriding (polymorphism) in action.
