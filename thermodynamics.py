def relative_volatility(T, P, light, heavy):
    K_light = light.psat(T) / P
    K_heavy = heavy.psat(T) / P
    alfa = K_light / K_heavy
    return alfa


def bubble_point_temperature(x_light, P, light, heavy, T_low=-150.0, T_high=250.0, tol=1e-8, max_iter=200):
    x_heavy = 1 - x_light

    def residual(T):
        return x_light * light.psat(T) + x_heavy * heavy.psat(T) - P

    f_low = residual(T_low)
    f_high = residual(T_high)

    for _ in range(max_iter):
        T_mid = (T_low + T_high) / 2
        f_mid = residual(T_mid)

        if abs(f_mid) < tol:
            return T_mid

        if f_low * f_mid < 0:
            T_high = T_mid
            f_high = f_mid
        else:
            T_low = T_mid
            f_low = f_mid

    return (T_low + T_high) / 2


def compute_rmin(alfa, zF, xD):
    y_feed_eq = (alfa * zF) / (1 + (alfa - 1) * zF)

    if xD <= y_feed_eq:
        Rmin = 0.0
    else:
        m_rec_min = (xD - y_feed_eq) / (xD - zF)
        Rmin = m_rec_min / (1 - m_rec_min)

    return Rmin, y_feed_eq
