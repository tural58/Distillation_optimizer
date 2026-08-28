import warnings


def validate_inputs(F, zF, xD, xB, Eo, tray_spacing):
    if F <= 0:
        raise ValueError("Feed flow rate F must be greater than zero.")

    if not (0 < zF < 1):
        raise ValueError("Feed composition zF must be between 0 and 1.")

    if not (0 < xD < 1):
        raise ValueError("Distillate composition xD must be between 0 and 1.")

    if not (0 < xB < 1):
        raise ValueError("Bottoms composition xB must be between 0 and 1.")

    if not (xB < zF < xD):
        raise ValueError(
            "For this separation, compositions must satisfy xB < zF < xD."
        )

    if not (0 < Eo <= 1):
        raise ValueError(
            "Overall tray efficiency Eo must be greater than 0 and at most 1."
        )

    if tray_spacing <= 0:
        raise ValueError("Tray spacing must be greater than zero.")

    if Eo < 0.2:
        warnings.warn(
            "Very low tray efficiency may result in an impractically large number of trays."
        )

    if tray_spacing < 0.3:
        warnings.warn("Tray spacing is unusually small.")

    if tray_spacing > 1.2:
        warnings.warn("Tray spacing is unusually large.")

    if xD > 0.95:
        warnings.warn(
            "xD is close to the ethanol-water azeotropic composition; results may be unrealistic."
        )

    if xB < 0.01:
        warnings.warn("xB is very close to zero; results may be unrealistic.")

    if (xD - zF) < 0.02 or (zF - xB) < 0.02:
        warnings.warn("The requested separation is very small.")
