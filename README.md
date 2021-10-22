# Llama CLI

A utility program that fetches and preprocesses learning data from supported learning
tools. Educators and researches have important usecases for accessing the raw data
that is generated while learners are using digital learning tools and environments.
These stakeholders can aim to e.g. analyse and improve teaching materials, methods,
and activities.

The aim of Llama CLI is to support and ease the steps of
1. connecting to the supported learning data sources
2. excluding persons and unwanted data tables or columns
3. fetching partial and complete data sets
4. anonymizing data before research activities
5. standardizing/transforming/sharing data
6. sampling and selecting data for analysis/ML

Currently supported data sources are
* A-plus https://apluslms.github.io/
* *TODO* Acos
* *TODO* Iwdap (course system prototype)

## Etymology

The name for the project comes from ~ la lumière à Montagne analytique. Pardon my French for ~ light on the mountain of analytics. Also LA is an acronym, that the
package author may have used in his thesis more than a decent number of times,
and that stands for Learning Analytics which is a research field in education
technologies. Llamas are also known from a controversial programming exercise for
computer science majors at Aalto University.

## Installation

Llama CLI is available at PyPI. It has a number of automatically installed
dependencies, most notably `pandas`, `numpy`, `scipy`, and `requests`.

      % python3 -m pip install llama-cli
      % llama

OR contained in a virtual environment (directory)

      % python3 -m venv .venv && .venv/bin/pip install llama-cli
      % .venv/bin/llama


## Instructions

Llama CLI operates on the current working directory. The configurations and data
will be stored in that directory – little bit like when working with git repositories.
One work directory can connect with multiple data sources and one should select
the sources that the current research or analysis project requires.

      % llama
      Llama CLI fetches and preprocesses learning data

      usage: llama <cmd> [<args>]

         status      Show the working tree status
         source      Manage sources for learning data
         list        List available data tables and columns
         privacy     Configure privacy (default: pseudoanonymous)
         exclude     Exclude selected tables, columns, or persons at fetch
         fetch       Fetch data from sources
         anonymize   Export anonymized data
         shell       Open python REPL with 'llama' instance for exported data

1. Use `llama source add` to interactively connect with data sources.
   The required addresses and keys will be prompted when required.
2. Use `llama list` to fetch the available data tables.
3. Time to consider excluding some uninteresting data or persons who have
   not consent to the research at hand. See `llama exclude` for examples.
4. Use `llama fetch rows` to download data tables. Depending on the project
   it may be necessary to also `llama fetch files` and/or `llama fetch meta`.
   This step has a delay between internet requests and it may take a long time
   to complete. The rows can be fetched again to append new data if supported
   by the data source.
5. The data in `fetched` directory is pseudoanonymized by default.
   The pseudo identifiers are required to complete fetching of depended data.
   With access to the source database the pseudo identifiers can be traced to persons.
   Use `llama anonymize` to produce `export` directory that can be e.g. stored in
   research repository, when the security measures and research consent allow it.


## Output & Research

The raw CSV and other files are available in the `export` directory. However,
the package also offers a Python interface for programmatic accessors and samplers
of the exported data. Exports can be opened both in an interactive test via
`llama shell` or using following constructor in a program or e.g. Jupyter notebook.

      from llama import LlamaApi
      llama = LlamaApi('export')

API documentation:

### `llama = LlamaApi(*directories)`

Constructs a standard interface to work with one or multiple Llama export directories.
If no parameters are given the constructor seeks `./export` directory.

* `*directories: str` (optional 0-N paramaters) Llama export directory paths
* **Returns** an instance of `LlamaApi`

### `llama.list(select)`

Lists sources and tables from the data. Subset of data can be selected with
the optional select dictionary.

* `select: dict` (optional) with keys
  * `source: int OR int[]` (optional) index of a learning data source
    OR list of indexes
  * `table: str OR str[]` (optional) table id prefixed with `#` (e.g. #1032)
    OR text to math against table name OR list of the previous
  * `files: bool` (optional) True to include only tables that link to files
    (e.g. submitted code) OR False to include only tables that do not link to files
* **Returns** list of `ids_and_names: dict[]`

The following methods all take an optional `select: dict` (identical with the
`llama.list` method) to access a subset of data and combine the reading of data
with further processing of it. The distinct processing methods can be found
separately from `LlamaStats`. They take outputs from other methods as parameters
(such as table rows from `llama.get`). A program that does multiple processing
tasks performs better when separately reading data, while the `llama.*`
convenience methods require less typing for quick results.

### `llama.get(select)`

Reads and iterates over data form tables.

* `select: dict` (optional) see `llama.list`
* **Returns** iterator over tuples of form
  `(source: dict, table: dict, rows: pandas.DataFrame)`

### `llama.exercise_series(select)`

Creates data series of interest for each selected table
(that are presumed to represent exercise submissions).

* `select: dict` (optional) see `llama.list`
* **Returns** iterator over `measures: dict` with keys
  * `best_grade: pandas.Series`
  * `first_grade: pandas.Series`
  * `every_grading: pandas.Series`
  * `attempts: pandas.Series`
  * `start_to_end_minutes: pandas.Series`
  * `grade_changes: pandas.Series`
  * `first_revision_minutes: pandas.Series`
  * `first_revision_grades: pandas.Series`
  * `second_revision_minutes: pandas.Series`
  * `second_revision_grades: pandas.Series`
  * `third_revision_minutes: pandas.Series`
  * `third_revision_grades: pandas.Series`

### `llama.execise_description(select)`

Calculates statistical measures of the exercise data series for each selected table.

* `select: dict` (optional) see `llama.list`
* **Returns** iterator over `pandas.DataFrame` that include statistical description
  for exercise data series (from `llama.exercise_series`)

### `llama.exercise_pdf(pdf_name, select)`

Plots pdf visualization of the exercise data series for each selected table.

* `pdf_name: str` (optional) default `exercises.pdf`
* `select: dict` (optional) see `llama.list`
* **Returns** None
