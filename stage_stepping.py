import numpy as np


def inverse_eqcurve(y, alfa):
    return y / (alfa - y * (alfa - 1))


def step_stages(xD, xB, zF, alfa, R, m_strip, b_strip, max_stages=500):
    x_current, y_current = xD, xD
    x_list = []
    y_list = []

    x_list.append(xD)
    y_list.append(xD)

    while x_current > xB and len(x_list) <= max_stages:
        x_current = inverse_eqcurve(y_current, alfa)

        if x_current > zF:
            y_current = (R / (R + 1)) * x_current + xD / (R + 1)
        else:
            y_current = m_strip * x_current + b_strip

        x_list.append(x_current)
        y_list.append(y_current)

    return x_list, y_list


def feed_stage_index(x_list, zF):
    for i in range(1, len(x_list)):
        if x_list[i] <= zF:
            return i
    return None


def find_pinch_point(alfa, zF, q):
    # """Find intersection of q-line with equilibrium curve (the pinch point)."""
    if abs(q - 1) < 1e-9:  # vertical q-line special case
        x_p = zF
    else:
        m_q = q / (q - 1)
        b_q = -zF / (q - 1)
        A = m_q * (alfa - 1)
        B = m_q + b_q * (alfa - 1) - alfa
        C = b_q
        roots = np.roots([A, B, C])
        real_roots = roots[np.isreal(roots)].real
        # keep the physically valid root: strictly between 0 and 1
        valid = [r for r in real_roots if 0 < r < 1]
        if not valid:
            raise ValueError(f"No physically valid pinch point found for q={q}")
        x_p = min(valid, key=lambda r: abs(r - zF))  # closest to zF as sanity pick
    y_p = (alfa * x_p) / (1 + (alfa - 1) * x_p)
    return x_p, y_p