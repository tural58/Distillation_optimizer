def relative_vol(T, P, light, heavy):
    K_light = light.psat(T) / P
    K_heavy = heavy.psat(T) / P
    alfa = K_light / K_heavy
    return alfa
