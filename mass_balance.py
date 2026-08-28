def overall_massbalance(F, zF, xD, xB):
    D = F * (zF - xB) / (xD - xB)
    B = F - D
    return B, D
