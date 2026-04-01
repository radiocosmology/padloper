#!/usr/bin/env python3
import argparse
import padloper as p

parser = argparse.ArgumentParser()
parser.add_argument("username")
parser.add_argument("groups", nargs="*",
                    help="a list of groups to put the user in")
parser.add_argument("-c", "--comment", default="",
                    help="comment to attach to the user")
parser.add_argument("-d", "--deactivate", action="store_true",
                    help="rather than creating a new user, deactivate an "\
                         "existing user")
parser.add_argument("-m", "--master-username", default="master",
                    help="the user with which to add the new user")
parser.add_argument("-f", "--force", action="store_true",
                    help="if the user already exists, replace it with the "\
                         "specified groups, rather than failing.")
arg = parser.parse_args()

p.set_user(arg.master_username)

if not arg.deactivate:
    groups = [p.UserGroup.from_db(g) for g in arg.groups]
    user = p.User(name=arg.username, groups=groups)
    try:
        user.add(strict_add=True)
        print("Added user \"%s\"." % (arg.username))
    except p.VertexAlreadyAddedError:
        if arg.force:
            old = p.User.from_db(arg.username)
            old.replace(user)
            print("Replaced existing user \"%s\" with new version." %\
                  arg.username)
        else:
            print("User \"%s\" already exists; doing nothing." %\
                  (arg.username))
else:
    if len(arg.groups) > 0:
        raise ValueError("There should be no groups when -f flag "\
                         "is invoked.")
    user = p.User.from_db(arg.username)
    print("Are you sure you want to disable user \"%s\"?" % arg.username)
    cont = input("Answer \"yes\" to continue or anything else to abort: ")
    if cont != "yes":
        print("Exiting")
    user.disable()
    print("User \"%s\" disabled." % arg.username)

