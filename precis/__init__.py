from .cfg import config
from .loader import *

from owlready2 import *

# Getting and loading the ontology
ont = get_ontology(config.ont_source).load()

# Binding to config module
config.ont = ont

# Extracting ontology object property relations
obj_property_list = []
for obj_property in config.ont.object_properties():
    obj_property_list += [str(obj_property).split('.')[1]]

# Removing 'hasDescription' from this list, as it has a special handler
obj_property_list.remove('hasDescription')

# Binding to config module
config.obj_properties = obj_property_list
