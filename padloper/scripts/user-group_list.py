#!/usr/bin/env python3
import argparse
import padloper as p

print("Groups:")
for g in p.UserGroup.get_list():
    print("  %s:" % g.name)
    for perm in g.permissions:
        print("    %s" % perm)
    print()

print()

print("Users (groups):")
for u in p.User.get_list():
    print("  %s (%s)" % (u.name, ", ".join([g.name for g in u.groups])))
