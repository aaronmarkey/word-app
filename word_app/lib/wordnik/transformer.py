# mypy: disable-error-code="name-defined"
import datetime
import re
from typing import Self

from wordnik.models import *  # noqa: F403

from word_app.lib.wordnik.models import (  # noqa
    Bigram,
    Citation,
    ContentProvider,
    Definition,
    Example,
    ExampleSearchResults,
    ExampleUsage,
    Facet,
    Label,
    Note,
    Related,
    ScoredWord,
    Sentence,
    TextPron,
)


def deserialize(obj, objClass):
    """Copied from Worknik's Python3 library.

    https://github.com/wordnik/wordnik-python3/blob/b4ae1e8007bf4e5eff43ab22d46911b5f0e7faf2/wordnik/swagger.py#L29

    This method is a complete mess. At somepoint I should rewrite it.
    """

    # Have to accept objClass as string or actual type. Type could be a
    # native Python type, or one of the model classes.
    if type(objClass) is str:
        if "list[" in objClass:
            match = re.match(r"list\[(.*)\]", objClass)
            subClass = match.group(1)
            return [deserialize(subObj, subClass) for subObj in obj]

        if objClass in [
            "int",
            "float",
            "dict",
            "list",
            "str",
            "bool",
            "datetime",
        ]:
            objClass = eval(objClass)
        else:  # not a native type, must be model class
            objClass = eval(objClass + "." + objClass)

    if objClass in [int, float, dict, list, str, bool]:
        return objClass(obj)
    elif objClass == datetime:
        # Server will always return a time stamp in UTC, but with
        # trailing +0000 indicating no offset from UTC. So don't process
        # last 5 characters.
        return datetime.datetime.strptime(obj[:-5], "%Y-%m-%dT%H:%M:%S.%f")

    instance = objClass()

    for attr, attrType in instance.swaggerTypes.items():
        if attr in obj:
            value = obj[attr]
            if attrType in ["str", "int", "float", "bool"]:
                attrType = eval(attrType)
                try:
                    value = attrType(value)
                except UnicodeEncodeError:
                    value = value.encode("utf-8")
                setattr(instance, attr, value)
            elif attrType == "datetime":
                setattr(
                    instance,
                    attr,
                    datetime.datetime.strptime(value[:-5], "%Y-%m-%dT%H:%M:%S"),
                )
            elif "list[" in attrType:
                match = re.match("list\[(.*)\]", attrType)
                subClass = match.group(1)
                subValues = []
                if not value:
                    setattr(instance, attr, None)
                else:
                    for subValue in value:
                        subValues.append(deserialize(subValue, subClass))
                setattr(instance, attr, subValues)
            else:
                setattr(instance, attr, deserialize(value, objClass))

    return instance


class WordnikTransformer:
    def defintions(self: Self, response: list[dict]) -> list[Definition]:  # noqa: F405
        return deserialize(response, "list[Definition]")

    def example_search_result(self: Self, response: dict) -> list[Example]:  # noqa: F405
        results = deserialize(response, "ExampleSearchResults")
        return results.examples

    def bigrams(self: Self, response: list[dict]) -> list[Bigram]:
        return deserialize(response, "list[Bigram]")

    def related(self: Self, response: list[dict]) -> list[Related]:  # noqa: F405
        return deserialize(response, "list[Related]")
