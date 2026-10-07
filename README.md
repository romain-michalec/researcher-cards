# Researcher cards

Turns Heriot-Watt University researcher profiles on the Pure research portal into plain text summaries called researcher cards: one Markdown file per person, with YAML frontmatter for the short facts and sections for the longer text.

The cards are the input to a Claude Project used to match researchers to Horizon Europe funding opportunity areas. They are uploaded to the Project alongside one file per area. Every text field is copied verbatim from the portal, and a thin profile gives a thin card, never a padded one.

The material for that Project is kept here too, in `matcher/`, for convenience. It is not part of the pipeline.

## Dependencies

This program is developed and tested on Linux with Python 3.12. It should work on macOS as well and with Python 3.11 to 3.15. Its dependencies are commonplace and straightforward:

* [Requests](https://requests.readthedocs.io/), to fetch the portal pages.
* [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/), to parse them.
* [PyYAML](https://pyyaml.org/), to write the card frontmatter.

Create a Python virtual environment, activate it, and install the dependencies into it:

```shell
python3 -m venv --upgrade-deps --prompt researcher-cards .venv
source .venv/bin/activate
python3 -m pip install requests beautifulsoup4 pyyaml
```

For a repeatable install, with the exact versions of the recurse dependencies used during development, install from `requirements.txt` instead:

```shell
python3 -m pip install -r requirements.txt
```

## Run

```shell
python3 researcher_cards.py
```

A failed fetch is reported on the standard error stream and the run carries on.

### Input

`heriot-watt.csv`, one academic per line with no header:

```csv
Firstname Lastname,email@hw.ac.uk,pure-slug
```

The slug is the last part of the person's portal URL, `https://researchportal.hw.ac.uk/en/persons/<slug>/`.

### Output

`cards/<slug>.md`: one card per person.

### Cache

The fetched portal pages are written into `~/.cache/researcher-cards/<slug>/` so that later runs of `python3 researcher_cards.py` make no requests. A page more than a month old is fetched again. Delete a person's folder to fetch their pages sooner.

## Files

The program:

* `researcher_cards.py`: Entry point: reads the CSV and runs the following files for each person.
* `fetch.py`: Fetches portal pages politely and caches them.
* `parse.py`: Turns cached pages into card fields.
* `write.py`: Writes a card in Markdown format.

Its input:

* `heriot-watt.csv`: A list of academics at Heriot-Watt University.
* `edinburgh.csv`: Placeholder file (not used yet).

Its output:

* `cards/`: The generated cards, to upload to the Project.

The matcher:

* `matcher/areas/`: Markdown files describing the opportunity areas, to upload to the Project.
* `matcher/instructions.md`: Instructions to paste into the Project.
* `matcher/examples.md`: Example questions for the Project, and checks with known answers.
