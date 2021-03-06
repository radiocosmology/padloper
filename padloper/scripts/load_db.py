from structure import *

from random import randrange, sample, randint

from time import time

if __name__ == "__main__":

    types_count = 10

    property_types_count = 3

    versions_per_type_count = 5

    components_per_version_count = 10

    for i in range(types_count):
        t = ComponentType(name=f"TYPE-{i}", comments=f"{i}th type")

        ptypes = []

        for k in range(property_types_count):
            pt = PropertyType(
                name=f"PTYPE-{i}-{k}", 
                units="u", 
                allowed_regex=".*", 
                n_values=1, 
                allowed_types=[t]
            )

            pt.add()
            
            ptypes.append(pt)

        rev_numbers = sample(
            range(1, 100), 
            versions_per_type_count
        )

        for j in range(versions_per_type_count):
            r = None

            if j < versions_per_type_count - 1: 
                r = ComponentVersion(
                    name=f"REV-{rev_numbers[j]}",
                    comments=f"{j}th version of {i}th type",
                    allowed_type=t
                )

            for k in range(components_per_version_count):
                c = Component(
                    name=f"CMP-{i}-{j}-{k}",
                    component_type=t,
                    version=r
                )
                c.add()

                for l in range(property_types_count):
                    p = Property(
                        values=[str(randint(0, 10))],
                        property_type=ptypes[l]
                    )
                    c.add_property(p, time=int(time()), uid="Anatoly")
                    
