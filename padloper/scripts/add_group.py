#!/usr/bin/env python3
import argparse
import padloper as p

parser = argparse.ArgumentParser()
parser.add_argument("groupname")
parser.add_argument("permissions", nargs="*",
                    help="a list of permissions to grant the group")
parser.add_argument("-c", "--comment", default="",
                    help="comment to attach to the user group")
parser.add_argument("-d", "--deactivate", action="store_true",
                    help="rather than creating a new group, deactivate an "\
                         "existing group")
parser.add_argument("-m", "--master-username", default="master",
                    help="the user with which to add the new user")
parser.add_argument("-f", "--force", action="store_true",
                    help="if the group already exists, replace it with the "\
                         "specified permissions, rather than failing.")
arg = parser.parse_args()

p.set_user(arg.master_username)

if not arg.deactivate:
    group = p.UserGroup(name=arg.groupname, permissions=arg.permissions)
    try:
        group.add(strict_add=True)
        print("Added group \"%s\"." % (arg.groupname))
    except p.VertexAlreadyAddedError:
        if arg.force:
            old = p.UserGroup.from_db(arg.groupname)
            old.replace(group)
            print("Replaced existing group \"%s\" with new version." %\
                  arg.groupname)
        else:
            print("Group \"%s\" already exists; doing nothing." %\
                  (arg.groupname))
else:
    if len(arg.permissions) > 0:
        raise ValueError("There should be no permissions when -f flag "\
                         "is invoked.")
    group = p.UserGroup.from_db(arg.groupname)
    print("Are you sure you want to delete user group \"%s\"?" %\
          arg.groupname)
    print("This will remove the group from all users currently in it.")
    cont = input("Answer \"yes\" to continue or anything else to abort: ")
    if cont != "yes":
        print("Exiting")
    cont = input("Please confirm again with \"yes\": ")
    if cont != "yes":
        print("Exiting")
    group.disable()
    print("User group \"%s\" disabled." % arg.groupname)

