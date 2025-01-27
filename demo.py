"""
Fastener Analysis Library Demo

This demo shows the core functionality of the fastener analysis library,
demonstrating:
1. Material creation and properties
2. Component creation
3. Junction assembly
4. Unit handling
"""

from units_config import ureg
from materials.standard_materials import GenericSteel, GenericAluminum
from components.threaded_components import Fastener, Nut
from components.clamped_components import Washer, PlateComponent
from junctions.junction import Junction

def main():
    """Run the demonstration."""
    print("Fastener Analysis Library Demo")
    print("==============================")

    # Create materials
    print("\n1. Creating Materials")
    print("--------------------")
    steel = GenericSteel()
    aluminum = GenericAluminum()
    print(f"Steel: {steel.identify()}")
    print(f"Aluminum: {aluminum.identify()}")

    # Create components
    print("\n2. Creating Components")
    print("--------------------")
    
    # Create a fastener
    bolt = Fastener(
        thread_spec="1/4-20",
        length=2.0 * ureg.inch,
        threaded_length=1.5 * ureg.inch,
        head_diameter=0.5 * ureg.inch,
        head_height=0.25 * ureg.inch,
        is_flat=False,
        tool_size="3/8",
        material=steel
    )
    print(f"Bolt: 1/4-20 x {bolt.length:~P}")

    # Create washers
    washer1 = Washer(
        inner_diameter=0.28 * ureg.inch,
        outer_diameter=0.75 * ureg.inch,
        thickness=0.05 * ureg.inch,
        material=steel
    )
    print(f"Washer: {washer1.thickness:~P} thick")

    # Create plates
    plate = PlateComponent(
        thickness=0.5 * ureg.inch,
        material=aluminum
    )
    print(f"Plate: {plate.thickness:~P} {plate.material.identify()}")

    # Create nut
    nut = Nut(
        thread_spec="1/4-20",
        width_across_flats=0.5 * ureg.inch,
        height=0.25 * ureg.inch,
        material=steel
    )
    print(f"Nut: {nut.thread_spec}")

    # Assemble junction
    print("\n3. Creating Junction")
    print("------------------")
    junction = Junction(
        fastener=bolt,
        clamped_components=[washer1, plate, washer1],
        threaded_member=nut
    )
    
    print(f"Stack-up thickness: {junction.calculate_stack_up():~P}")
    print(f"Grip length: {junction.grip_length:~P}")

    print("\nDemo complete!")

if __name__ == "__main__":
    main()