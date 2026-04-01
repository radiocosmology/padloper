"""
permissions.py

Classes for managing users and permissions.
"""

from typing import Optional, List
import _global as g
from _base import Vertex, strictraise
from _edges import RelationUserGroup
from _exceptions import *
from gremlin_python.process.graph_traversal import __, constant

#import time
#import re
#from unicodedata import name

#import warnings
#from xmlrpc.client import boolean
#from attr import attr, attributes
#from gremlin_python.process.traversal import Order, P, TextP
#from sympy import true

permissions_set = {
    # Component:
    # protected
    'Component;add',
    'Component;replace',
    'Component;unset_property',
    'Component;replace_property',
    'Component;disable_property',
    'Component;disconnect',
    'Component;disable_connection',
    'Component;disable_subcomponent',
    'Component;subcomponent_connect',
    
    # general
    'Component;connect',
    'Component;set_property',

    # unprotected
    # 'Component;get_property',
    # 'Component;get_all_properties',
    # 'Component;get_all_properties_of_type',
    # 'Component;get_connections',
    # 'Component;get_list',
    # 'Component;get_count',
    # 'Component;get_all_flags',
    # 'Component;get_subcomponents',
    # 'Component;get_subcomponent',
    # 'Component;get_supercomponents',
    # 'Component;added_to_db',
    # 'Component;from_db',
    # 'Component;from_id',
    # 'Component;as_dict',

    # Component types:
    # protected
    'ComponentType;add',
    'ComponentType;replace',

    # unprotected
    # 'ComponentType;as_dict',
    # 'ComponentType;added_to_db',
    # 'ComponentType;from_db',
    # 'ComponentType;from_id',
    # 'ComponentType;get_names_of_types_and_versions',
    # 'ComponentType;get_list',
    # 'ComponentType;get_count',

    # Component version:
    # protected
    'ComponentVersion;add',
    'ComponentVersion;replace',

    # unprotected
#     'ComponentVersion;as_dict',
#     'ComponentVersion;added_to_db',
#     'ComponentVersion;from_db',
#     'ComponentVersion;from_id',
#     'ComponentVersion;get_list',
#     'ComponentVersion;get_count',

    # PropertyType:
    # protected
    'PropertyType;add',
    'PropertyType;replace',

    # Property:
    # protected
    'Property;_add',

    # FlagType:
    # protected
    'FlagType;add',
    'FlagType;replace',

    # FlagSeverity:
    # protected
    'FlagSeverity;add',
    'FlagSeverity;replace',

    # Flag:
    # protected
    'Flag;replace',

    # general
    'Flag;add',
    'Flag;end_flag',
}

def check_permission(permission, class_name, method_name):
    print(f"{class_name};{method_name}")
    if permission is None:
        # check for global variable
        # if user is a string:
            # user = User.from_db(name=user)
        
        # user to be stored as a user vertex
        try:
            user = g._user['id']
        except Exception as e:
            raise NoPermissionsError(
            "User not set."
            )
        
        if isinstance(user, str):
            user = User.from_db(name=user)
        permission = user.get_permissions()
        # check permissions
    
    # raise error if user does not have all required permissions

    # check default permissions (logged in as a valid user)
    # if not '*' in permission:
    #     raise NoPermissionsError("Invalid user. Account must be validated by an admin.")
    
    if f"{class_name};{method_name}" in permissions_set and f"{class_name};{method_name}" not in permission:
        raise NoPermissionsError(
            "User does not have the required permissions to perform this action."
        )

    # if not all(perm in permission for perm in permission_mapping[f"{class_name};{method_name}"]):
    #         raise NoPermissionsError(
    #         "User does not have the required permissions to perform this action."
    #         )


class User(Vertex):
    """
    The representaiton of a user vertex. Contains a name attirbute,
    and institution attribute.

    :ivar name: The username of the user.
    :ivar institution: The institution the user belongs to.
    """

    category: str = "User"

    name: str
    institution: str

    def __new__(cls, name: str, institution: str,
                id: int = g._VIRTUAL_ID_PLACEHOLDER):
        """
        Return a User instance given the desired attributes.

        :param name: Name used by the user to login.
        :type name: str

        :param institution: Name of the institution of the user.
        :type institution: str

        :param allowed_group: The UserGroup instance representing the groups
          the user is in.
        :type user_group: List[UserGroup]

        :param id: The serverside ID of the User, defaults to
          _VIRTUAL_ID_PLACEHOLDER
        :type id: int,optional 
        """
        if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
            return g._vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(self, name: str, institution: str,
                id: int = g._VIRTUAL_ID_PLACEHOLDER):
        """
        Initialize a User instance.

        :param id: The ID of the user.
        :type id: int
        :param name: The username of the user.
        :type name: str
        :param institution: The institution the user belongs to.
        :type institution: str
        """
        self.name = name
        self.institution = institution
        super().__init__(id)

    def add(self, strict_add=False):
        """
        Add the user to the serverside database.
        """
        # If already added, raise an error!
        if self.added_to_db():
            strictraise(strict_add, VertexAlreadyAddedError,
                f"User with username {self.name}" +
                " already exists in the database."
            )
            return self.from_db(self.name)
        
        attributes = {
            'name': self.name,
            'institution': self.institution
        }

        super().add(attributes)

        # add to default user group (must be set from init_user-groups.py)
        default_group = UserGroup.from_db('Default')
        self.set_user_group(default_group)

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a User instance based on username

        :param name: Name used by the user to login.
        :type name: str 
        """
        try:
            d = g.t.V().has('category', User.category)\
                    .has('name', name).as_('v').valueMap()\
                    .as_('props').select('v').id().as_('id').select('props', 'id')\
                    .next()
        except:
            raise UserNotAddedError
        
        props, id_ = d['props'], d['id']
        
        # TODO: get user groups

        Vertex._cache_vertex(
            User(
                name=name,
                institution=props['institution'][0],
                id=id_
            )
        )

        return g._vertex_cache[id_]
    

    def added_to_db(self) -> bool:
        """Check if this user is added to the database."""
        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or
            g.t.V().has('category', User.category)\
            .has('name', self.name)\
            .count().next() > 0
        )
    
    def set_user_group(self, group, strict_add: bool=True):
        """
        Given a UserGroup :param group, connect this User to this group.

        :param group: A UserGroup to connect this User to
        :type group: UserGroup
        """
        if not self.added_to_db():
            raise UserNotAddedError(
                f"User {self.name} has not yet been added to the database."
            )
        
        if not group.added_to_db():
            raise UserGroupNotAddedError(
                f"UserGroup {group.name} has not yet been added to the database."
            )
        
        group_edge = RelationUserGroup(
            inVertex=self,
            outVertex=group
        )

        group_edge._add()

    def get_user_groups(self):
    
        if not self.added_to_db():
            raise UserNotAddedError(
                f"User {self.name} has not yet been added to the database."
            )

        query = g.t.V(self.id()).bothE(RelationUserGroup.category)\
                .as_('e').valueMap().as_('edge_props')\
                .select('e').otherV().id_().as_('vertex_id')\
                .select('edge_props', 'vertex_id').toList()
        
        # Build up the result 
        result = []
        for q in query:
            group = UserGroup.from_id(q['vertex_id'])
            edge = RelationUserGroup(
                inVertex=group,
                outVertex=self,
            )
            result.append([group, edge])

        return result

    def get_permissions(self) -> set:
        # store perms
        perms = []

        groups = self.get_user_groups()
        for group in groups:
            group_perms = group[0].permissions
            perms.extend(group_perms)

        # # make unique
        return list(set(perms))
    
    @classmethod
    def get_list(cls):
        # t = g.t.V().has('category', User.category).toList()
        # print(t)
        traversal = g.t.V().has('category', User.category)
        us = traversal.range(0, 1000)\
            .project('id', 'name', 'institution')\
            .by(__.id_()) \
            .by(__.values('name')) \
            .by(__.values('institution')) \
            .toList()

        users = []
        for entry in us:
            id, name, institution = entry['id'], entry.get('name'), entry.get('institution')
            users.append(User(name, institution))

        return users
    
    def as_dict(self):
        """"Return a dictionary representation of this User."""
        return {
            'name': self.name,
            'institution': self.institution
        }


class UserGroup(Vertex):
    """
    Represents a user group vertex in JanusGraph.

    :ivar name: The name of the user group.
    """

    category: str = "UserGroup"
    
    name: str
    permissions: List[str]

    # def __new__(cls, name: str, permissions: List[str],
    #             id: int = g._VIRTUAL_ID_PLACEHOLDER):
    #     """
    #     Return a UserGroup instance given the name, and permission list.

    #     :param name: The name of the user group.
    #     type name: str

    #     :param permissions: The list of permissions, as strings.
    #     :type permissions: List[str]
    #     """
    #     if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
    #         return g._vertex_cache[id]
    #     else:
    #         return object.__new__(cls)

    def __init__(self, name: str, permissions: List[str],
                 id: int = g._VIRTUAL_ID_PLACEHOLDER):
        """
        Initialize a UserGroup instance.

        :param name: The name of the user group.
        :type name: str
        :param permissions: This list of permissions.
        :type permissions: List[str]
        :param id: The ID of the user group.
        :type id: int
        """
        # If the user passes a string rather than a list of strings, fix it.
        if isinstance(permissions, str):
            permisisons = [permissions]

        self.name = name
        self.permissions = permissions
        Vertex.__init__(self, id=id)

    def _add(self, strict_add=False):
        """
        Add the user group vertex to the serverside database.
        """
        if self.added_to_db():
            strictraise(strict_add, VertexAlreadyAddedError,
                f"UserGroup with name {self.name}" +
                " already exists in the database."
            )
            return self.from_db(self.name)
        
        attributes = {
            'name': self.name,
            'values': self.permissions
        }

        Vertex.add(self, attributes)
        return self.from_db(self.name)
    
    def as_dict(self):
        """"Return a dictionary representation of this UserGroup."""
        return {
            'name': self.name,
            'permissions': self.permissions
        }
    
    
    @classmethod
    def from_db(cls, name: str):
        """Query the databse and return a UserGroup instance based on name.
        
        :param name: Name used to identify the UserGroup
        :type name: str
        """
        try:
            d = g.t.V().has('category', UserGroup.category)\
                    .has('name', name).as_('v').valueMap()\
                    .as_('props').select('v').id().as_('id').select('props', 'id')\
                    .next()
        except:
            raise UserGroupNotAddedError
        
        props, id_ = d['props'], d['id']

        Vertex._cache_vertex(
            UserGroup(
                name=name,
                permissions=props['values'][0],
                id=id_
            )
        )

        return g._vertex_cache[id_]
    
    @classmethod
    def from_id(self, id: int):
        """Given and ID of a serverside UserGroup vertex, return a UserGroup instance."""

        if id not in g._vertex_cache:
            d = g.t.V(id).project('permissions', 'name')\
            .by(__.properties('values').value().fold())\
            .by(__.values('name')).next()

            permissions, name = d['permissions'], d.get('name')

            if not isinstance(permissions, list):
                permissions = [permissions]


            Vertex._cache_vertex(
                UserGroup(
                    name=name,
                    permissions=permissions,
                    id=id
                )
            )

        return g._vertex_cache[id]

    
    def added_to_db(self) -> bool:
        """Check if this UserGroup is added to the database."""
        return (
            self.id() != g._VIRTUAL_ID_PLACEHOLDER or
            g.t.V().has('category', UserGroup.category)\
            .has('name', self.name)\
            .count().next() > 0
        )
    
    @classmethod
    def get_list(cls):
        traversal = g.t.V().has('category', UserGroup.category)
        gps = traversal.range(0, 1000)\
            .project('id', 'name', 'permissions')\
            .by(__.id_())\
            .toList()
        
        groups = []
        for entry in gps:
            id = entry['id']
            UserGroup.from_id(id)
            groups.append(UserGroup.from_id(id))

        return groups
        

class Permission(object):
    _permission_list = []
    _user_id = None

    def __init__(self, permission_list, uid):
        self._permission_list = permission_list
        self._user_id = uid

    def get_permission_list(self):
        return self._permission_list
    
    def get_user_id(self):
        return self._user_id


# class Permission(Vertex):
#     """ The representation of a permission.

#     :ivar name: The name of the permission.
#     :ivar comments: Comments about the permission.
#     """

#     category: str = 'permission'

#     name: str
#     comments: str

#     def __new__(cls, name: str, comments: str = '',
#                 id: int = g._VIRTUAL_ID_PLACEHOLDER):
#         """
#         Return a Permission instance given the desired attributes.

#         :param name: The name of the permission.
#         :type name: str

#         :param comments: The comments attached to this permission, defaults to ""
#         :type comments: str

#         :param id: The serverside ID of the permission, defaults to
#           _VIRTUAL_ID_PLACEHOLDER
#         :type id: int, optional
#         """

#         if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
#             return g._vertex_cache[id]

#         else:
#             return object.__new__(cls)

#     def __init__(self, name: str, comments: str = " ",
#                  id: int = g._VIRTUAL_ID_PLACEHOLDER):
#         """
#         Initialize a Permission instance given the desired attributes.

#         :param name: The name of the permission.
#         :type name: str

#         :param comments: The comments attached to this permission, defaults to ""
#         :type comments: str

#         :param id: The serverside ID of the permission, defaults to 
#           _VIRTUAL_ID_PLACEHOLDER
#         :type id: int, optional
#         """

#         self.name = name
#         self.comments = comments

#         Vertex.__init__(self, id=id)

#     def add(self, strict_add=False):
#         """Add this permission to the database."""

#         # if already added, raise an error!
#         if self.added_to_db():
#             # strictraise(strict_add,VertexAlreadyAddedError,
#             #     f"Permission with name {self.name}" +
#             #     "already exists in the database."
#             # )
#             return self.from_db(self.name)

#         attributes = {
#             'name': self.name,
#             'comments': self.comments
#         }

#         Vertex.add(self=self, attributes=attributes)

#         print(f"Added {self}")
#         return self

#     def added_to_db(self) -> bool:
#         """
#         Return whether this Permission is added to the database, that is, whether the ID is not the Virtual ID placeholder and perform a query to the database to determine if the vertex has already been added.

#         :return: True if element is added to database, False otherwise.
#         :rtype: bool
#         """

#         return (
#             self.id() != g._VIRTUAL_ID_PLACEHOLDER or (\
#                 g.t.V().has('category', Permission.category)\
#                    .has('name', self.name).count().next() == 1 \
#             )
#         )

#     @classmethod
#     def from_db(cls, name: str):
#         """Query the database and return a Permission instance based on permission :param name.

#         :param name: The name of the permission.
#         :type name: str

#         :return: A Permission instance with the correct name, comments, and ID.
#         :rtype: Permission
#         """

#         try:
#             d = g.t.V().has('category', Permission.category)\
#                    .has('name', name) \
#                    .as_('v').valueMap().as_('props')\
#                    .select('v').id_().as_('id') \
#                    .select('props', 'id').next()
#         except StopIteration:
#             raise PermissionNotAddedError

#         props, id = d['props'], d['id']
#         print(props)

#         Vertex._cache_vertex(
#             Permission(
#                 name=name,
#                 comments=props['comments'][0],
#                 id=id
#             )
#         )

#         return g._vertex_cache[id]

#     @classmethod
#     def from_id(cls, id: int):
#         """ Query the database and return a Permission instance based on the ID.

#         :param id: The serverside ID of the Permission vertex.
#         :type id: int

#         :return: Return a Perimssion from that ID.
#         :rtype: Permission
#         """

#         if id not in g._vertex_cache:
#             d = g.t.V(id).valueMap().next()

#             Vertex._cache_vertex(
#                 Permission(
#                     name=d['name'][0],
#                     comments=d['comments'][0],
#                     id=id
#                 )
#             )

#         return g._vertex_cache[id]


# class UserGroup(Vertex):
#     """ The representation of a user group.

#     :ivar name: The name of the user group.
#     :ivar comments: The comments assocaited with the group.
#     :ivar permission: A list of Perimssion instances associated with this group.
#     """

#     category: str = 'user_group'

#     name: str
#     comments: str
#     permission: List[Permission]

#     def __init__(self, name: str, comments: str, permission: List[Permission],
#                  id: int = g._VIRTUAL_ID_PLACEHOLDER):

#         self.name = name
#         self.comments = comments
#         self.permission = permission

#         if len(self.permission) == 0:
#             raise UserGroupZeroPermissionError(
#                 f"No permission were specified for user group {name}"
#             )

#         Vertex.__init__(self=self, id=id)

#     def add(self, strict_add=False):
#         """
#         Add this UserGroup instance to the database.
#         """

#         if self.added_to_db():
#             # strictraise(strict_add, VertexAlreadyAddedError,
#             #     f"UserGroup with name {self.name}" +
#             #     "already exists in the database."
#             # )
#             return self.from_db(self.name)


#         attributes = {
#             'name': self.name,
#             'comments': self.comments
#         }

#         Vertex.add(self=self, attributes=attributes)

#         for p in self.permission:

#             if not p.added_to_db():
#                 p.add()

#             e = RelationGroupAllowedPermission(
#                 inVertex=p,
#                 outVertex=self
#             )

#             e.add()
#         print(f"Added {self}")
#         return self

#     def added_to_db(self) -> bool:
#         """Return whether this UserGroup is added to the database, that is, whether the ID is not the virtual ID placeholder and perform a query to the database to determine if the vertex has already been added.

#         :return: True if element is added to database, False otherwise.
#         :rtype: bool
#         """

#         return (
#             self.id() != g._VIRTUAL_ID_PLACEHOLDER or (\
#                 g.t.V().has('category', UserGroup.category)\
#                     .has('name', self.name).count().next() == 1 \
#             )
#         )

#     @classmethod
#     def from_db(cls, name: str):
#         """Query the database and return a UserGroup instance based on the name :param name:, connected to the necessary Permission instances.

#         :param name: The name of the UserGroup instance.
#         :type name: str
#         """


#         try:
#             d = g.t.V().has('category', UserGroup.category).has('name', name) \
#                    .project('id', 'attrs', 'permission_ids').by(__.id_()) \
#                    .by(__.valueMap()) \
#                    .by(__.both(RelationGroupAllowedPermission.category).id_() \
#                    .fold()).next()
#         except StopIteration:
#             raise UserGroupNotAddedError

#         id, attrs, perimssion_ids = d['id'], d['attrs'], d['permission_ids']

#         if id not in g._vertex_cache:

#             permissions = []

#             for p_id in perimssion_ids:
#                 permissions.append(Permission.from_id(p_id))

#             Vertex._cache_vertex(
#                 UserGroup(
#                     name=name,
#                     comments=attrs['comments'][0],
#                     permission=permissions,
#                     id=id
#                 )
#             )

#         return g._vertex_cache[id]




# class User(Vertex):
#     """ The representation of a user.

#     :ivar uname: Name used by the user to login.
#     :ivar allowed_group: Optional allowed user group of the user vertex, as a
#         list of UserGroup attributes.
#     """

#     category: str = "user"

#     uname: str
#     pwd_hash: str
#     institution: str
#     allowed_group: List[UserGroup] = None

#     def __new__(cls, uname: str, pwd_hash: str, institution: str,
#                 allowed_group: List[UserGroup] = None,
#                 id: int = g._VIRTUAL_ID_PLACEHOLDER):
#         """
#         Return a User instance given the desired attributes.

#         :param uname: Name used by the user to login.
#         :type uname: str

#         :param pwd_hash: Password is stored after being salted and hashed.
#         :type pwd_hash: str

#         :param institution: Name of the institution of the user.
#         :type institution: str

#         :param allowed_group: The UserGroup instance representing the groups
#           the user is in.
#         :type user_group: List[UserGroup]

#         :param id: The serverside ID of the User, defaults to
#           _VIRTUAL_ID_PLACEHOLDER
#         :type id: int,optional 
#         """
#         if id is not g._VIRTUAL_ID_PLACEHOLDER and id in g._vertex_cache:
#             return g._vertex_cache[id]

#         else:
#             return object.__new__(cls)

#     def __init__(self, uname: str, pwd_hash: str, institution: str,
#                  allowed_group: List[UserGroup] = None,
#                  id: int = g._VIRTUAL_ID_PLACEHOLDER):
#         """
#         Initialize a User instance given the desired attributes.

#         :param uname: Name used by the user to login.
#         :type uname: str

#         :param pwd_hash: Password is stored after being salted and hashed.
#         :type pwd_hash: str

#         :param institution: Name of the institution of the user.
#         :type institution: str

#         :param allowed_group: The UserGroup instance representing the groups the user is in.
#         :type user_group: List[UserGroup]

#         :param id: The serverside ID of the User, defaults to 
#           _VIRTUAL_ID_PLACEHOLDER
#         :type id: int,optional 
#         """

#         self.uname = uname
#         self.pwd_hash = pwd_hash
#         self.institution = institution
#         self.allowed_group = allowed_group

#         Vertex.__init__(self, id=id)

#     def add(self, strict_add=False):
#         """Add this user to the serverside.
#         """

#         # If already added, raise an error!
#         if self.added_to_db():
#             strictraise(strict_add,VertexAlreadyAddedError,
#                 f"User with username {self.uname}" +
#                 "already exists in the database."
#             )
#             return self.from_db(self.name)


#         attributes = {
#             'uname': self.uname,
#             'pwd_hash': self.pwd_hash,
#             'institution': self.institution
#         }

#         Vertex.add(self, attributes)

#         if self.allowed_group is not None:

#             for gtype in self.allowed_group:

#                 if not gtype.added_to_db():
#                     gtype.add()

#                 e = RelationUserAllowedGroup(
#                     inVertex=gtype,
#                     outVertex=self
#                 )

#                 e.add()

#         print(f"Added {self}")
#         return self


#     def added_to_db(self) -> bool:
#         """Return whether this User is added to the database, that is, whether the ID is not the virtual ID placeholder and perform a query to the database if the vertex has already been added.

#         :return: True if element is added to database, False otherwise.
#         rtype: bool
#         """

#         return (
#             self.id() != g._VIRTUAL_ID_PLACEHOLDER or (
#                 g.t.V().has('category', User.category)\
#                    .has('uname', self.uname).count().next() > 0
#             )
#         )

#     @classmethod
#     def _attrs_to_user(cls, uname: str, pwd_hash: str, institution: str,
#                        allowed_group: List[UserGroup] = None,
#                        id: int = g._VIRTUAL_ID_PLACEHOLDER):
#         """Given the id and attributes of a User, see if one exists in the cache. If so, return the cached User. Otherwise, create a new one, cache it, and return it.

#         :param uname: Name used by the user to login.
#         :type uname: str

#         :param pwd_hash: Password is stored after being salted and hashed.
#         :type pwd_hash: str

#         :param institution: Name of the institution of the user.
#         :type institution: str

#         :param allowed_group: The UserGroup instance representing the groups the user is in.
#         :type user_group: List[UserGroup]

#         :param id: The serverside ID of the User, defaults to 
#           _VIRTUAL_ID_PLACEHOLDER
#         :type id: int,optional 
#         """

#         if id not in g._vertex_cache:
#             Vertex._cache_vertex(
#                 User(
#                     uname=uname,
#                     pwd_hash=pwd_hash,
#                     institution=institution,
#                     allowed_group=allowed_group,
#                     id=id
#                 )
#             )

#         return g._vertex_cache[id]

#     @classmethod
#     def from_db(cls, uname: str):
#         """Query the database and return a User instance based on uname

#         :param uname: Name used by the user to login.
#         :type uname: str 
#         """

#         try:
#             d = g.t.V().has('category', User.category).has('uname', uname) \
#                    .project('id', 'attrs', 'group_ids').by(__.id_()) \
#                    .by(__.valueMap()) \
#                    .by(__.both(RelationUserAllowedGroup.category).id_().fold())\
#                    .next()
#         except StopIteration:
#             raise UserNotAddedError

#         # to access attributes from attrs, do attrs[...][0]
#         id, attrs, gtype_ids = d['id'], d['attrs'], d['group_ids']

#         if id not in g._vertex_cache:

#             gtypes = []

#             for gtype_id in gtype_ids:
#                 gtypes.append(UserGroup.from_id(gtype_id))

#             Vertex._cache_vertex(
#                 User(
#                     uname=uname,
#                     pwd_hash=attrs['pwd_hash'][0],
#                     institution=attrs['institution'][0],
#                     allowed_group=gtypes,
#                     id=id
#                 )
#             )

#         return g._vertex_cache[id]

#     @classmethod
#     def from_id(cls, id: int):
#         """Query the database and return a User instance based on the ID.

#         :param id: The serverside ID of the User instance vertex.
#         type id: int
#         :return: Return a User from that ID.
#         rtype: User
#         """

#         if id not in g._vertex_cache:

#             d = g.t.V(id).project('attrs', 'group_ids').by(__.valueMap())\
#                    .by(__.both(RelationUserAllowedGroup.category).id_().fold())\
#                    .next()

#             # to access attributes from attrs, do attrs[...][0]

#             attrs, gtype_ids = d['attrs'], d['group_ids']

#             gtypes = []

#             for gtype_id in gtype_ids:
#                 gtypes.append(UserGroup.from_id(gtype_id))

#             Vertex._cache_vertex(
#                 User(
#                     uname=attrs['uname'][0],
#                     pwd_hash=attrs['pwd_hash'][0],
#                     institution=attrs['institution'][0],
#                     allowed_group=gtypes,
#                     id=id
#                 )
#             )

#         return g._vertex_cache[id]
