# Abaco Schemas

This is a common library of JSON schemas for validating JSON deserialized
from Abaco Messages. These are referenceable inside a Reactor at
`/abacomessages/SchemaName.json`. To add another schema, issue a pull
request that includes the Draft 4 schema document and 2-3 example JSON
messages that validate against it as per this [JSONschema Validator][1]

## Example

Schema

```json
{
    "$schema": "http://json-schema.org/draft-04/schema#",
    "$id": "https://sd2e.github.io/reactors-user-guide/schemas/message.json",
    "title": "AbacoMessage",
    "description": "Generic Abaco JSON message",
    "type": "object"
}
```

Test Data

```json
[{
        "schema": "AbacoMessage.json",
        "object": {
            "key": "value"
        },
        "validates": true
    },
    {
        "schema": "AbacoMessage.json",
        "object": [{
            "key": "value"
        }],
        "validates": false
    },
    {
        "schema": "AbacoMessage.json",
        "object": [],
        "valid": false
    }
]```

[1]: https://www.jsonschemavalidator.net/
