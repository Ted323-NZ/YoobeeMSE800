# Week 5 - Activity 5: Inheritance 2 (Animal System)

## Project Purpose
This project demonstrates object-oriented inheritance using an animal classification system.

## UML Structure Implemented
- Animal (base class) -> Mammal, Bird, Fish
- Mammal -> Dog, Cat
- Bird -> Eagle, Penguin
- Fish -> Salmon, Shark

## Design Overview
- Animal contains shared attribute: name
- Mammal/Bird/Fish inherit Animal and add shared attribute: feature
- Specific animals (Dog/Cat/Eagle/Penguin/Salmon/Shark) implement behavior methods:
  - Dog/Cat: walk()
  - Eagle: fly()
  - Penguin/Salmon/Shark: swim()

## Run
python3 main.py
