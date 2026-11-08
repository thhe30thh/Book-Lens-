# BookLens

BookLens is a literary knowledge discovery and recommendation
system that explores connections between books, authors,
themes, philosophical ideas, and literary movements.

## Current status

Milestone 0: Application foundation.

Implemented:
- Flask application factory
- Environment configuration
- Web homepage
- JSON health endpoint
- API error handling
- Automated tests with pytest

## Technology

- Python 3.12
- Flask
- HTML5
- CSS3
- pytest

## Setup

Clone the repository and enter the project directory.

Create a virtual environment:

    python3 -m venv .venv

Activate it:

    source .venv/bin/activate

Install dependencies:

    pip install -r requirements-dev.txt

## Run

    python run.py

Open:

    http://127.0.0.1:5000/

## Run tests

    pytest -v

## Project structure

    booklens/
        api/
        web/
            templates/
            static/
        config.py
    tests/
        api/
    legacy/

## Planned features

- Literary knowledge database
- Book and author discovery
- Thematic relationship modeling
- Explainable recommendations
- Interactive literary knowledge graph
