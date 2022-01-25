"""
exceptions.py

Contains declarations of custom exceptions.
"""


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class VertexAlreadyAddedError(Error):
    """
    Exception raised when a vertex is to be added that has already been added
    to the database.
    """
    pass


class EdgeAlreadyAddedError(Error):
    """
    Exception raised when an edge is trying to be accessed that has not been
    added to the database.
    """
    pass


class EdgeNotAddedError(Error):
    """
    Exception raised when an edge is trying to be accessed that has not been
    added to the database.
    """
    pass


class ComponentNotAddedError(Error):
    """
    Exception raised when trying to access a component from the database
    that is not added to the database.
    """
    pass


class ComponentTypeNotAddedError(Error):
    """
    Exception raised when trying to access a component type from the database
    that is not added to the database.
    """
    pass


class ComponentRevisionNotAddedError(Error):
    """
    Exception raised when trying to access a component revision when its
    allowed type has not been added to the database.
    """
    pass


class ComponentsAlreadyConnectedError(Error):
    """
    Exception raised when trying to connect two components when they are already
    connected.
    """
    pass

class ComponentsAlreadyDisconnectedError(Error):
    """
    Exception raised when trying to disconnect two components when they are
    already disconnected.
    """
    pass

class ComponentConnectToSelfError(Error):
    """
    Exception raised when trying to connect a component to itself.
    """
    pass


class PropertyTypeZeroAllowedTypesError(Error):
    """
    Exception raised when trying to create a property type with zero allowed
    component types.
    """
    pass


class PropertyTypeNotAddedError(Error):
    """
    Exception raised when a property type has not been added to the serverside.
    """
    pass


class PropertyNotAddedError(Error):
    """
    Exception raised when trying to access a property when its allowed
    type has not been added to the database.
    """
    pass


class PropertyIsSameError(Error):
    """
    Exception raised when trying to set a property of a component when the
    values of the new property are the same as the values of the existing
    property.
    """
    pass


class PropertyWrongNValuesError(Error):
    """
    Exception raised when trying to create a property in which the number of
    values is different from the n_values attribute of the property's
    corresponding property type.
    """
    pass


class PropertyNotMatchRegexError(Error):
    """
    Exception raised when a value of the property does not match the
    allowed regex of the associated property type.
    """
    pass

class UnassignedError(Error):
    """
    Exception raised when something unexpected occurs, but should still
    have an error.
    """
    pass