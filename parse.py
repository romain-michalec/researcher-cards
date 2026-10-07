"""Turn cached Pure portal pages into researcher card fields."""

from bs4 import BeautifulSoup, Tag

from fetch import BASE_URL

AFFILIATION = "div.rendering_person_personorganisationlistrendererportal"  # holds job title, school and department
SECTIONS = {  # portal heading, spelled exactly as on the portal, to card field
    "Biography": "biography",
    "Research interests": "interests",
    "Research Grants and Projects": "grants",
}


def parse_person(slug, profile_html, fingerprints_html):
    """Turn a person's cached portal pages into card fields, None where absent."""
    profile = BeautifulSoup(profile_html, "html.parser")
    fingerprints = BeautifulSoup(fingerprints_html, "html.parser")

    return {
        "title": text_of(profile, f"{AFFILIATION} span.job-title"),
        "school": text_of(profile, f"{AFFILIATION} a.school"),
        "department": text_of(profile, f"{AFFILIATION} a.department"),
        "pure": f"{BASE_URL}{slug}/",
        "orcid": link_of(profile, "div.rendering_person_personorcidrendererportal a.orcid"),
        "scopus": link_of(profile, 'a[href*="scopus.com/authid/"]'),
        **parse_sections(profile),
        "keywords": parse_keywords(profile),
        "fingerprints": parse_fingerprints(fingerprints),
        "selected_outputs": parse_selected_outputs(profile),
    }


def parse_sections(soup):
    """Return the biography, interests and grants sections as plain text, None where absent."""
    fields = dict.fromkeys(SECTIONS.values())

    for heading in soup.select("div.rendering_person_profileinformationportal h3.subheader"):
        field = SECTIONS.get(heading.get_text(strip=True))
        block = heading.find_next_sibling()
        if field and block is not None:
            fields[field] = block_text(block)

    return fields


def parse_keywords(soup):
    """Return the keywords people chose themselves, or None if there are none."""
    # The other items in the group are library classification codes such as "QA75 ...".
    items = soup.select("div.keyword-group li.userdefined-keyword")
    return [item.get_text(strip=True) for item in items] or None


def parse_fingerprints(soup):
    """Return each fingerprint concept with its vocabulary and displayed weight, in page order."""
    concepts = []
    for group in soup.select("div.person-fingerprint-thesauri"):
        vocabulary = text_of(group, "h3")
        for item in group.select("li.concept-badge-small-container"):
            concepts.append({
                "name": text_of(item, "span.concept"),
                "vocabulary": vocabulary,
                "weight": text_of(item, "span.value"),
            })

    return concepts or None


def parse_selected_outputs(soup):
    """Return title, date and author line of each research output shown on the profile page."""
    outputs = []
    for output in soup.select("div.rendering_researchoutput_portal-short"):
        outputs.append({
            "title": text_of(output, "h3.title"),
            "date": text_of(output, "span.date"),
            "authors": author_line(output),
        })

    return outputs or None


def author_line(output):
    """Return the author line as shown, which is all the text between the title and the date."""
    title = output.select_one("h3.title")
    if title is None:
        return None

    parts = []
    for node in title.next_siblings:
        if isinstance(node, Tag) and "date" in node.get("class", []):
            break
        parts.append(node.get_text() if isinstance(node, Tag) else str(node))

    return " ".join("".join(parts).split()).rstrip(",") or None


def block_text(block):
    """Flatten a text block: paragraphs separated by blank lines, list items as "- " lines."""
    paragraphs = []
    for element in block.find_all(["p", "li"]) or [block]:
        text = " ".join(element.get_text().split())
        if text:
            paragraphs.append(f"- {text}" if element.name == "li" else text)

    return "\n\n".join(paragraphs)


def text_of(soup, selector):
    """Return the text of the first element matching selector, or None."""
    element = soup.select_one(selector)
    return element.get_text(strip=True) if element else None


def link_of(soup, selector):
    """Return the href of the first link matching selector, or None."""
    element = soup.select_one(selector)
    return element["href"] if element else None
