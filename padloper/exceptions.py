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


class FlagNotAddedError(Error):
    """
    Exception raised when trying to access a flag from the database that is not added to the database.
    """
    pass


class ComponentsAlreadyConnectedError(Error):
    """
    Exception raised when trying to connect two components when they are already
    connected.
    """
    pass


class ComponentAlreadySubcomponentError(Error):
    """
    Exception raised when trying to connect two components when one of them is already a subcomponent of other.
    """
    pass


class ComponentIsSubcomponentOfOtherComponentError(Error):
    """
    Exception raised when trying to connect two components when one of them is already a subcomponent of other.
    """
    pass


class ComponentsAlreadyDisconnectedError(Error):
    """
    Exception raised when trying to disconnect two components when they are
    already disconnected.
    """
    pass


class ComponentsConnectBeforeExistingConnectionError(Error):
    """
    Exception raised when trying to connect two components before another
    existing connection.
    """
    pass


class ComponentsOverlappingConnectionError(Error):
    """
    Exception raised when trying to connect two components at overlapping times
    with another connection of the two components.
    """
    pass


class ComponentConnectToSelfError(Error):
    """
    Exception raised when trying to connect a component to itself.
    """
    pass


class ComponentSubcomponentToSelfError(Error):
    """
    Exception raised when trying to make a component subcomponent to itself.
    """
    pass


class ComponentPropertiesOverlappingError(Error):
    """
    Exception raised when trying to set a property for a component 
    at overlapping times with another property of the same type.
    """
    pass


class ComponentSetPropertyBeforeExistingPropertyError(Error):
    """
    Exception raised when trying to set a property for a component
    before another existing property of the same type.
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


class ComponentPropertyStartTimeExceedsInputtedTime(Error):
    """
    Exception raised when the end time inputted by the user
    is later than the component's property start time.
    """


class UserZeroAllowedTypesError(Error):
    """
    Exception raised when creating a user with zero allowed group types. 
    """


class UserGroupZeroPermissionError(Error):
    """
    Exception raised when creating a UserGroup instance with zero allowed permission. 
    """
