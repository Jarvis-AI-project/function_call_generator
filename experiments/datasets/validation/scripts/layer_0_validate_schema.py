"""
This script validates the schema of a json document using `schema.json` file.
"""

import json
from jsonschema import validate, ValidationError, SchemaError

def validate_schema(
    document: dict,
    schema: dict = json.load(open("schema.json", "r", encoding="utf-8"))
):
    """
    Validates the schema of a json document using `schema.json` file.
    """
    try:
        validate(document, schema)
    except ValidationError as error:
        return False, error
    except SchemaError as error:
        return False, error
    return True, None
