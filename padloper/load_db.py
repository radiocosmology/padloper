from structure import *

from random import randrange, sample

if __name__ == "__main__":
    for i in range(10):
        t = ComponentType(name=f"TYPE-{i}", comments=f"{i}th type")

        num_revisions = 10

        rev_numbers = sample(range(1, 16), num_revisions)

        for j in range(num_revisions):
            r = None

            if j < num_revisions - 1: 
                r = ComponentRevision(
                    name=f"REV-{rev_numbers[j]}",
                    comments=f"{j}th revision of {i}th type",
                    allowed_type=t
                )

            for k in range(100):
                c = Component(
                    name=f"CMP-{i}-{j}-{k}",
                    component_type=t,
                    revision=r
                )
                c.add()