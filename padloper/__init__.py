# For relative imports to work in Python 3.6
# https://stackoverflow.com/a/49375740
CONTINUE HERE: get all the importing working properly.
import os, sys; sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from base import *
from edges import *
from exceptions import *
from permissions import *
from component_nodes import *
from property_nodes import *
from flag_nodes import *
