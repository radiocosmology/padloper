from structure import *

from random import randrange, sample

if __name__ == "__main__":
    for i in range(10):
        t = ComponentType(name=f"TYPE-{i}", comments=f"{i}th type")

        rev_numbers = sample(range(1, 16), 3)

        for j in range(4):
            r = None

            if j < 3: 
                r = ComponentRevision(
                    name=f"REV-{rev_numbers[j]}",
                    comments=f"{j}th revision of {i}th type",
                    allowed_type=t
                )

            for k in range(3):
                c = Component(
                    name=f"CMP-{i}-{j}-{k}",
                    component_type=t,
                    revision=r
                )
                c.add()