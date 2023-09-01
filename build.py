import markdown
import shutil
import os
import csv
from typing import List

_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "template")
_BUILD_DIR = os.path.join(os.path.dirname(__file__), "build")


def create_dir_silently(path: str):
    """Create a directory if it doesn't exist."""
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def generate_collection(collection_filename: str, card_template: str) -> List[str]:
    """Generate a collection of cards from a CSV file.

    The CSV file should have the following columns:
        - card-title
        - card-description
        - card-image
        - card-alt-alt
        - card-link
        - card-other-classes
        - card-tags

    Returns:
        A list of HTML cards
    """
    cards = []
    with open(collection_filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row["card-description"] = markdown.markdown(
                row["card-description"], extensions=["nl2br"]
            )
            row["card-tags"] = "".join(
                [str(markdown.markdown(tag)) for tag in row["card-tags"].split(":")]
            )
            new_card = card_template[:]
            for key, value in row.items():
                new_card = new_card.replace("{{" + key + "}}", value)
            cards.append(new_card)
    return cards


def main(collection_filename: str = "collections/collection.csv"):
    """Build the index.html file and copy the assets directory."""
    create_dir_silently(_BUILD_DIR)

    with open(os.path.join(_TEMPLATE_DIR, "index.html"), "r") as f:
        index = f.read()

    with open(os.path.join(_TEMPLATE_DIR, "card.html"), "r") as f:
        card_template = f.read()

    cards = generate_collection(collection_filename, card_template)
    index = index.replace("<!-- {{ collection }} -->", "\n".join(cards))

    with open(os.path.join(_BUILD_DIR, "index.html"), "w") as f:
        f.write(index)

    shutil.copytree(
        os.path.join(_TEMPLATE_DIR, "assets"), _BUILD_DIR, dirs_exist_ok=True
    )

if __name__ == "__main__":
    main()
    print("Build completed in {0}".format(_BUILD_DIR))
