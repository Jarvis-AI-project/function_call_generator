"""
This script validates the schema of a json document using `schema.json` file.
"""

from jsonschema import validate, ValidationError, SchemaError

def validate_schema(
    document: dict,
    schema: dict
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
