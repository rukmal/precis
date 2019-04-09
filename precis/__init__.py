from .cfg import config
from .loader import *

from owlready2 import *

# Getting and loading the ontology
ont = get_ontology(config.ont_source).load()

# Binding to config module
config.ont = ont

# Extracting ontology object property relations
object_properties = {}
for object_property in config.ont.object_properties():
    object_property_name = str(object_property).split('.')[1] 
    object_properties[object_property_name] = object_property

# Removing 'hasDescription' from this dict, as it has a special handler
del object_properties['hasDescription']

# Binding to config module
config.obj_properties = object_properties


# Extracting ontology classes and building class -> constructor map
ont_classes = dict()
for ont_class in config.ont.classes():
    # Getting class name
    class_name = str(ont_class).split('.')[1]
    ont_classes[class_name] = ont_class

# Binding to config module
config.ont_classes = ont_classes


# Extracting ontology data properties list
data_properties = dict()
for data_property in config.ont.data_properties():
    data_property_name = str(data_property).split('.')[1]
    data_properties[data_property_name] = data_property

# Binding to config module
config.data_properties = data_properties
