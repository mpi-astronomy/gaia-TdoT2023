import markdown
import shutil
import os
import csv
import yaml
from typing import List, Callable, TypeVar


try:
    from typing import deprecated
except ImportError:
    _T = TypeVar("_T")

    def deprecated(__msg: str) -> Callable[[_T], _T]:
        """Indicate that a class, function or overload is deprecated.
        Usage:
            @deprecated("Use B instead")
            class A:
                pass
            @deprecated("Use g instead")
            def f():
                pass
            @overload
            @deprecated("int support is deprecated")
            def g(x: int) -> int: ...
            @overload
            def g(x: str) -> int: ...
        When this decorator is applied to an object, the type checker
        will generate a diagnostic on usage of the deprecated object.
        No runtime warning is issued. The decorator sets the ``__deprecated__``
        attribute on the decorated object to the deprecation message
        passed to the decorator. If applied to an overload, the decorator
        must be after the ``@overload`` decorator for the attribute to
        exist on the overload as returned by ``get_overloads()``.
        See PEP 702 for details.
        """

        def decorator(__arg: _T) -> _T:
            __arg.__deprecated__ = __msg
            return __arg

        return decorator


def create_dir_silently(path: str):
    """Create a directory if it doesn't exist."""
    try:
        os.mkdir(path)
    except FileExistsError:
        pass


def generate_collection_from_yaml(
    collection_filename: str, card_template: str
) -> List[str]:
    """Generate a collection of cards from a CSV file.

    The CSV file should have the following columns:
        - card-title
        - card-description
        - card-image
        - card-image-alt
        - card-link
        - card-other-classes
        - card-tags

    Returns:
        A list of HTML cards
    """
    cards = []
    with open("collections/collection.yaml", "r") as f:
        yamldata = yaml.load(f, yaml.SafeLoader)
        for row in yamldata:
            row["card-description"] = markdown.markdown(
                row.get("card-description", ""), extensions=["nl2br"]
            )
            row["card-tags"] = "".join(
                [str(markdown.markdown(tag)) for tag in row.get("card-tags", "")]
            )
            new_card = card_template[:]
            for key, value in row.items():
                new_card = new_card.replace("{{" + key + "}}", value)
            cards.append(new_card)
    return cards


@deprecated("Use generate_collection_from_yaml instead.")
def generate_collection_from_csv(
    collection_filename: str, card_template: str
) -> List[str]:
    """Generate a collection of cards from a CSV file.

    The CSV file should have the following columns:
        - card-title
        - card-description
        - card-image
        - card-image-alt
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


_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "template")
_BUILD_DIR = os.path.join(os.path.dirname(__file__), "build")


def main(collection_filename: str = "collections/collection.yaml"):
    """Build the index.html file and copy the assets directory."""
    create_dir_silently(_BUILD_DIR)

    with open(os.path.join(_TEMPLATE_DIR, "index.html"), "r") as f:
        index = f.read()

    with open(os.path.join(_TEMPLATE_DIR, "card.html"), "r") as f:
        card_template = f.read()

    cards = generate_collection_from_yaml(collection_filename, card_template)
    index = index.replace("<!-- {{ collection }} -->", "\n".join(cards))

    with open(os.path.join(_BUILD_DIR, "index.html"), "w") as f:
        f.write(index)

    shutil.copytree(
        os.path.join(_TEMPLATE_DIR, "assets"), _BUILD_DIR, dirs_exist_ok=True
    )


if __name__ == "__main__":
    main()
    print("Build completed in {0}".format(_BUILD_DIR))
