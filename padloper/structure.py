"""
permissions.py

Classes for managing users and permissions.
"""
import time
import re
from unicodedata import name

import warnings
from xmlrpc.client import boolean
from attr import attr, attributes

from gremlin_python.process.traversal import Order, P, TextP
from sympy import true
from graph_connection import g
from gremlin_python.process.graph_traversal import __, constant

from exceptions import *

from typing import Optional, List

from base import *

class Permission(Vertex):
    """ The representation of a permission.

    :ivar name: The name of the permission.
    :ivar comments: Comments about the permission.
    """

    category: str = 'permission'

    name: str
    comments: str

    def __new__(
            cls, name: str, comments: str = '', id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Return a Permission instance given the desired attributes.

        :param name: The name of the permission.
        :type name: str

        :param comments: The comments attached to this permission, defaults to ""
        :type comments: str

        :param id: The serverside ID of the permission, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(self, name: str, comments: str = " ", id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Initialize a Permission instance given the desired attributes.

        :param name: The name of the permission.
        :type name: str

        :param comments: The comments attached to this permission, defaults to ""
        :type comments: str

        :param id: The serverside ID of the permission, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int, optional
        """

        self.name = name
        self.comments = comments

        Vertex.__init__(self, id=id)

    def add(self, strict_add=False):
        """Add this permission to the database."""

        # if already added, raise an error!
        if self.added_to_db():
            strictraise(strict_add,VertexAlreadyAddedError,
                f"Permission with name {self.name}" +
                "already exists in the database."
            )
            return self.from_db(self.name)

        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

        print(f"Added {self}")
        return self

    def added_to_db(self) -> bool:
        """
        Return whether this Permission is added to the database, that is, whether the ID is not the Virtual ID placeholder and perform a query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', Permission.category).has(
                    'name', self.name).count().next() == 1
            )
        )

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a Permission instance based on permission :param name.

        :param name: The name of the permission.
        :type name: str

        :return: A Permission instance with the correct name, comments, and ID.
        :rtype: Permission
        """

        try:
            d = g.V().has('category', Permission.category).has('name', name) \
                .as_('v').valueMap().as_('props').select('v').id_().as_('id') \
                .select('props', 'id').next()
        except StopIteration:
            raise PermissionNotAddedError

        props, id = d['props'], d['id']

        Vertex._cache_vertex(
            Permission(
                name=name,
                comments=props['comments'][0],
                id=id
            )
        )

        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """ Query the database and return a Permission instance based on the ID.

        :param id: The serverside ID of the Permission vertex.
        :type id: int

        :return: Return a Perimssion from that ID.
        :rtype: Permission
        """

        if id not in _vertex_cache:
            d = g.V(id).valueMap().next()

            Vertex._cache_vertex(
                Permission(
                    name=d['name'][0],
                    comments=d['comments'][0],
                    id=id
                )
            )

        return _vertex_cache[id]


class UserGroup(Vertex):
    """ The representation of a user group.

    :ivar name: The name of the user group.
    :ivar comments: The comments assocaited with the group.
    :ivar permission: A list of Perimssion instances associated with this group.
    """

    category: str = 'user_group'

    name: str
    comments: str
    permission: List[Permission]

    def __init__(self, name: str, comments: str, permission: List[Permission], id: int = VIRTUAL_ID_PLACEHOLDER):

        self.name = name
        self.comments = comments
        self.permission = permission

        if len(self.permission) == 0:
            raise UserGroupZeroPermissionError(
                f"No permission were specified for user group {name}"
            )

        Vertex.__init__(self=self, id=id)

    def add(self, strict_add=False):
        """
        Add this UserGroup instance to the database.
        """

        if self.added_to_db():
            strictraise(strict_add, VertexAlreadyAddedError,
                f"UserGroup with name {self.name}" +
                "already exists in the database."
            )
            return self.from_db(self.name)


        attributes = {
            'name': self.name,
            'comments': self.comments
        }

        Vertex.add(self=self, attributes=attributes)

        for p in self.permission:

            if not p.added_to_db():
                p.add()

            e = RelationGroupAllowedPermission(
                inVertex=p,
                outVertex=self
            )

            e.add()
        print(f"Added {self}")
        return self

    def added_to_db(self) -> bool:
        """Return whether this UserGroup is added to the database, that is, whether the ID is not the virtual ID placeholder and perform a query to the database to determine if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        :rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', UserGroup.category).has(
                    'name', self.name).count().next() == 1
            )
        )

    @classmethod
    def from_db(cls, name: str):
        """Query the database and return a UserGroup instance based on the name :param name:, connected to the necessary Permission instances.

        :param name: The name of the UserGroup instance.
        :type name: str
        """

        try:
            d = g.V().has('category', UserGroup.category).has('name', name) \
                .project('id', 'attrs', 'permission_ids').by(__.id_()) \
                .by(__.valueMap()) \
                .by(__.both(RelationGroupAllowedPermission.category).id_() \
                .fold()).next()
        except StopIteration:
            raise UserGroupNotAddedError

        id, attrs, perimssion_ids = d['id'], d['attrs'], d['permission_ids']

        if id not in _vertex_cache:

            permissions = []

            for p_id in perimssion_ids:
                permissions.append(Permission.from_id(p_id))

            Vertex._cache_vertex(
                UserGroup(
                    name=name,
                    comments=attrs['comments'][0],
                    permission=permissions,
                    id=id
                )
            )

        return _vertex_cache[id]


class User(Vertex):
    """ The representation of a user.

    :ivar uname: Name used by the user to login.
    :ivar pwd_hash: Password is stored after being salted and hashed.
    :ivar institution: Name of the institution of the user. 
    :ivar allowed_group: Optional allowed user group of the user vertex, as a
        list of UserGroup attributes.
    """

    category: str = "user"

    uname: str
    pwd_hash: str
    institution: str
    allowed_group: List[UserGroup] = None

    def __new__(
        cls, uname: str, pwd_hash: str, institution: str, allowed_group: List[UserGroup] = None, id: int = VIRTUAL_ID_PLACEHOLDER
    ):
        """
        Return a User instance given the desired attributes.

        :param uname: Name used by the user to login.
        :type uname: str

        :param pwd_hash: Password is stored after being salted and hashed.
        :type pwd_hash: str

        :param institution: Name of the institution of the user.
        :type institution: str

        :param allowed_group: The UserGroup instance representing the groups the user is in.
        :type user_group: List[UserGroup]

        :param id: The serverside ID of the User, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int,optional 
        """
        if id is not VIRTUAL_ID_PLACEHOLDER and id in _vertex_cache:
            return _vertex_cache[id]

        else:
            return object.__new__(cls)

    def __init__(
            self, uname: str, pwd_hash: str, institution: str, allowed_group: List[UserGroup] = None, id: int = VIRTUAL_ID_PLACEHOLDER):
        """
        Initialize a User instance given the desired attributes.

        :param uname: Name used by the user to login.
        :type uname: str

        :param pwd_hash: Password is stored after being salted and hashed.
        :type pwd_hash: str

        :param institution: Name of the institution of the user.
        :type institution: str

        :param allowed_group: The UserGroup instance representing the groups the user is in.
        :type user_group: List[UserGroup]

        :param id: The serverside ID of the User, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int,optional 
        """

        self.uname = uname
        self.pwd_hash = pwd_hash
        self.institution = institution
        self.allowed_group = allowed_group

        Vertex.__init__(self, id=id)

    def add(self, strict_add=False):
        """Add this user to the serverside.
        """

        # If already added, raise an error!
        if self.added_to_db():
            strictraise(strict_add,VertexAlreadyAddedError,
                f"User with username {self.uname}" +
                "already exists in the database."
            )
            return self.from_db(self.name)


        attributes = {
            'uname': self.uname,
            'pwd_hash': self.pwd_hash,
            'institution': self.institution
        }

        Vertex.add(self, attributes)

        if self.allowed_group is not None:

            for gtype in self.allowed_group:

                if not gtype.added_to_db():
                    gtype.add()

                e = RelationUserAllowedGroup(
                    inVertex=gtype,
                    outVertex=self
                )

                e.add()

        print(f"Added {self}")
        return self


    def added_to_db(self) -> bool:
        """Return whether this User is added to the database, that is, whether the ID is not the virtual ID placeholder and perform a query to the database if the vertex has already been added.

        :return: True if element is added to database, False otherwise.
        rtype: bool
        """

        return (
            self.id() != VIRTUAL_ID_PLACEHOLDER or (
                g.V().has('category', User.category).has(
                    'uname', self.uname).count().next() > 0
            )
        )

    @classmethod
    def _attrs_to_user(
            cls, uname: str, pwd_hash: str, institution: str, allowed_group: List[UserGroup] = None, id: int = VIRTUAL_ID_PLACEHOLDER):
        """Given the id and attributes of a User, see if one exists in the cache. If so, return the cached User. Otherwise, create a new one, cache it, and return it.

        :param uname: Name used by the user to login.
        :type uname: str

        :param pwd_hash: Password is stored after being salted and hashed.
        :type pwd_hash: str

        :param institution: Name of the institution of the user.
        :type institution: str

        :param allowed_group: The UserGroup instance representing the groups the user is in.
        :type user_group: List[UserGroup]

        :param id: The serverside ID of the User, defaults to VIRTUAL_ID_PLACEHOLDER
        :type id: int,optional 
        """

        if id not in _vertex_cache:
            Vertex._cache_vertex(
                User(
                    uname=uname,
                    pwd_hash=pwd_hash,
                    institution=institution,
                    allowed_group=allowed_group,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_db(cls, uname: str):
        """Query the database and return a User instance based on uname

        :param uname: Name used by the user to login.
        :type uname: str 
        """

        try:
            d = g.V().has('category', User.category).has('uname', uname) \
                .project('id', 'attrs', 'group_ids').by(__.id_()) \
                .by(__.valueMap()) \
                .by(__.both(RelationUserAllowedGroup.category).id_().fold()) \
                .next()
        except StopIteration:
            raise UserNotAddedError

        # to access attributes from attrs, do attrs[...][0]
        id, attrs, gtype_ids = d['id'], d['attrs'], d['group_ids']

        if id not in _vertex_cache:

            gtypes = []

            for gtype_id in gtype_ids:
                gtypes.append(UserGroup.from_id(gtype_id))

            Vertex._cache_vertex(
                User(
                    uname=uname,
                    pwd_hash=attrs['pwd_hash'][0],
                    institution=attrs['institution'][0],
                    allowed_group=gtypes,
                    id=id
                )
            )

        return _vertex_cache[id]

    @classmethod
    def from_id(cls, id: int):
        """Query the database and return a User instance based on the ID.

        :param id: The serverside ID of the User instance vertex.
        type id: int
        :return: Return a User from that ID.
        rtype: User
        """

        if id not in _vertex_cache:

            d = g.V(id).project('attrs', 'group_ids').by(__.valueMap()).by(
                __.both(RelationUserAllowedGroup.category).id_().fold()).next()

            # to access attributes from attrs, do attrs[...][0]

            attrs, gtype_ids = d['attrs'], d['group_ids']

            gtypes = []

            for gtype_id in gtype_ids:
                gtypes.append(UserGroup.from_id(gtype_id))

            Vertex._cache_vertex(
                User(
                    uname=attrs['uname'][0],
                    pwd_hash=attrs['pwd_hash'][0],
                    institution=attrs['institution'][0],
                    allowed_group=gtypes,
                    id=id
                )
            )

        return _vertex_cache[id]
