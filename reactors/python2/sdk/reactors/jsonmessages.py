import json
import os
from jsonschema import validate, FormatChecker, ValidationError


HERE = os.path.dirname(os.path.abspath(__file__))
PWD = os.getcwd()
ROOT = '/'
MESSAGE_SCHEMA = os.path.join(HERE, 'message.jsonschema')


def _validate_return_bool(object_json, schema_json, permissive=True):

        class formatChecker(FormatChecker):
            def __init__(self):
                FormatChecker.__init__(self)

        try:
            validate(object_json, schema_json, format_checker=formatChecker())
            return True
        except Exception as e:
            if permissive is True:
                return False
            else:
                raise Exception(e)


def validate_message(messagedict,
                     messageschema=MESSAGE_SCHEMA,
                     permissive=True):
    """
    Validate dictonary derived from JSON string against a schema

    Positional arguments:
    messagedict - dict - JSON-derived object

    Keyword arguments:
    messageschema - str - path to the requisite JSON schema file
    permissive - bool - swallow validation errors [True]
    """
    try:
        with open(messageschema) as schema:
            schema_json = json.loads(schema.read())
    except Exception as e:
        if permissive is False:
            raise Exception("Schema error", e)
        else:
            return False

    return _validate_return_bool(messagedict,
                                 schema_json,
                                 permissive=permissive)
