import warnings

from compounds import PAIRS
from thermodynamics import bubble_point_temperature
from validation import validate_inputs
from column import DistillationColumn
from report import generate_report


def main():
    pair_names = list(PAIRS.keys())
    print("Available component pairs:")
    for i, name in enumerate(pair_names, start=1):
        print(f"{i}. {name}")
    choice = int(input("Select component pair [number]: "))
    pair_name = pair_names[choice - 1]
    light, heavy = PAIRS[pair_name]

    F = float(input("Feed flow rate F [kmol/h]: "))
    zF = float(input(f"Feed {light.name} mole fraction zF: "))
    xD = float(input(f"Distillate {light.name} mole fraction xD: "))
    xB = float(input(f"Bottoms {light.name} mole fraction xB: "))
    Eo = float(input("Overall tray efficiency Eo: "))
    tray_spacing = float(input("Tray spacing [m]: "))

    P = 1
    q = 1

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        validate_inputs(F, zF, xD, xB, Eo, tray_spacing)
        design_warnings = [str(w.message) for w in caught]

    T = bubble_point_temperature(zF, P, light, heavy)

    print(f"Operating temperature (feed bubble point) T = {T:.2f} C")

    column = DistillationColumn(
        F=F,
        zF=zF,
        P=P,
        T=T,
        q=q,
        xD=xD,
        xB=xB,
        Eo=Eo,
        tray_spacing=tray_spacing,
        light=light,
        heavy=heavy,
    )
    column.run()

    output_path = generate_report(column, "distillation_report.pdf", design_warnings=design_warnings)
    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    main()
