# Doctolib availability tracker

- [Doctolib availability tracker](#doctolib-availability-tracker)
- [1. 💬 Project description](#1--project-description)
- [2. 📟 Prerequisites](#2--prerequisites)
- [3. 🔌 Quickstart](#3--quickstart)
- [4. 🚀 Run](#4--run)
- [5. 🏆 Code Quality and Formatting](#5--code-quality-and-formatting)


# 1. 💬 Project description

A Selenium-based web scraper that monitors Doctolib for available medical appointments. The tool:

1. Searches appointments by specialty and location
2. Filters results by date, doctor name, and location
3. Sends email notifications with matching appointments

# 2. 📟 Prerequisites

- Install uv to handle python version and dependencies (`v0.5.10`).
- To receive notification by email, you must setup your google mail app password, see [how to](https://stackoverflow.com/questions/72478573/how-to-send-an-email-using-python-after-googles-policy-update-on-not-allowing-j)

**Environment variables**

- The environment variables can be set manually, or using a `.env` file is supported at the directory's root.
- An example is given in `.env-example`
- The environment variable will override the value set in `.env`

| Variable | Description | Required | Default | Examples |
|----------|-------------|----------|---------|-----------|
| `ENVIRONMENT` | Execution environment (`local`, `dev`, `preprod`, `prod`) | Yes | - | - |
| `SENDER_EMAIL` | Gmail account used to send email | Yes | - | - |
| `SENDER_GMAIL_PASSWORD` | Sender gmail app password used to send email, see [how to](https://stackoverflow.com/questions/72478573/how-to-send-an-email-using-python-after-googles-policy-update-on-not-allowing-j) | Yes | - | - |
| `RECEIVER_EMAIL` | Gmail account used to receive email | Yes | - | - |
| `SEARCH_TERM` | Search term to use in doctolib search page | Yes | - | `ORL` |
| `SEARCH_PLACE` | Search place to use in doctolib search page | Yes | - | `Paris`, `Agen` |
| `NB_DAYS_FILTER` | Appointments starting after this many days will be filtered | No | `14` | `90` |
| `RAW_FILTERED_DOCTOR_NAMES` | Doctor names to filter (case sensitive, separated by `\|`) | No | - | `Dupont`, `Dupont\|DURAND` |
| `RAW_FILTERED_CITIES` | Cities to filter (case sensitive, separated by `\|`) | No | - | `Périgueux`, `Périgueux\|Agen` |
| `HEADLESS` | To run selenium headless mode | No | `true` | `true`, `false` |


# 3. 🔌 Quickstart

1. Make sure the correct environment variables are set.
2. Install uv (v0.5.10 recommended). See [doc](https://docs.astral.sh/uv/getting-started/installation/). `curl -LsSf https://astral.sh/uv/0.5.10/install.sh | sh`
3. Install project and dependencies: `uv sync`
4. Set up pre-commit: `uv run pre-commit install -t commit-msg -t pre-commit`
5. Run script: `uv run python -m src.main`


# 4. 🚀 Run

The behavior are controlled through the environment variables, for instance to change the place and specialty, one can either:
- Set the env var manually
- Change the `.env` file
- Run the following:
```shell
(export search_place=Marseille; export search_term=Cardiologue; uv run python src/doctolib_availability_tracker/main.py)
```

# 5. 🏆 Code Quality and Formatting

- The python files are linted and formatted using ruff, see configuration in `pyproject.toml`
- Pre-commit configuration is available to ensure trigger quality checks (e.g. linter)
- Commit messages follow the conventional commit convention
