from structure import *

from random import randrange, sample

if __name__ == "__main__":

    types_count = 10

    revisions_per_type_count = 5

    components_per_revision_count = 5

    for i in range(types_count):
        t = ComponentType(name=f"TYPE-{i}", comments=f"{i}th type")

        rev_numbers = sample(
            range(1, 16), 
            revisions_per_type_count
        )

        for j in range(revisions_per_type_count):
            r = None

            if j < revisions_per_type_count - 1: 
                r = ComponentRevision(
                    name=f"REV-{rev_numbers[j]}",
                    comments=f"{j}th revision of {i}th type",
                    allowed_type=t
                )

            for k in range(components_per_revision_count):
                c = Component(
                    name=f"CMP-{i}-{j}-{k}",
                    component_type=t,
                    revision=r
                )
                c.add()