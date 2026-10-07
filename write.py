"""Write researcher cards as Markdown, with YAML frontmatter for the short facts."""

import yaml

FRONTMATTER = [  # in the order they appear in the card
    "name", "university", "title", "school", "department", "email",
    "pure", "orcid", "scopus", "keywords", "completeness",
]
ABSENT = "Not provided on the Pure profile."

# Write a missing value as "orcid:" rather than "orcid: null", which reads as jargon.
yaml.SafeDumper.add_representer(type(None), lambda dumper, _: dumper.represent_scalar("tag:yaml.org,2002:null", ""))


def write_card(card, path):
    """Write a researcher card as Markdown, with short facts in YAML frontmatter and long text below."""
    frontmatter = yaml.safe_dump(
        {field: card[field] for field in FRONTMATTER},
        sort_keys=False, allow_unicode=True, width=1000,
    )

    sections = [
        section("Biography", card["biography"]),
        section("Research interests", card["interests"]),
        section("Research grants and projects", card["grants"]),
        section("Fingerprints", fingerprints_text(card["fingerprints"])),
        section("Selected outputs", outputs_text(card["selected_outputs"])),
        "## Notes\n",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\n{frontmatter}---\n\n" + "\n".join(sections), encoding="utf-8")


def section(heading, text):
    """Return a Markdown section, saying so explicitly when the profile has nothing for it."""
    return f"## {heading}\n\n{text or ABSENT}\n"


def fingerprints_text(concepts):
    """Return fingerprint concepts as a Markdown list, or None if there are none."""
    if concepts is None:
        return None
    return "\n".join(f"- {c['name']} ({c['vocabulary']}) {c['weight']}" for c in concepts)


def outputs_text(outputs):
    """Return selected outputs as a Markdown list, or None if there are none."""
    if outputs is None:
        return None
    return "\n".join(f"- {o['title']} ({o['date']}). {o['authors']}" for o in outputs)
