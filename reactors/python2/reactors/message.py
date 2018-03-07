"""
Instantiate an AbacoMessage Object from the messsage using JSONschema
"""
import os
import yaml
from attrdict import AttrDict
import python_jsonschema_objects as pjs

# Look for local file message.json (or message.yml as JSON schema can be experessed as YAML)
# If not found, instantiate a dummy one

HERE = os.path.dirname(os.path.abspath(__file__))
PWD = os.getcwd()
ROOT = '/'
SCHEMA_FILE = 'message.json'

builder = None
ns = None

def read_schema():
    """
    Reads JSON schema into 'settings', allowing optional
    ENV-based overrides via namespaced variables
    """
    config = AttrDict()
    # File-based configuration.
    places = [ROOT, HERE]
    for p in places:
        fname = os.path.join(p, SCHEMA_FILE)
        if os.path.isfile(fname):
            try:
                with open(fname, "r") as conf:
                    try:
                        builder = pjs.ObjectBuilder(fname)
                        ns = builder.build_classes()
                    except Exception as e:
                            print("Error loading schema {}: {}".format(fname, e))
                            pass
                break
