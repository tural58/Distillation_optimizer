class Compound:
    def __init__(self, name, MW, A, B, C):
        self.name = name
        self.MW = MW
        self.A = A
        self.B = B
        self.C = C

    def psat(self, T):
        return (10 ** (self.A - self.B / (self.C + T))) / 760


ethanol = Compound("Ethanol", 46.07, 8.20417, 1642.89, 230.300)
water = Compound("Water", 18.02, 8.07131, 1730.63, 233.426)
isobutane = Compound("Isobutane", 58.12, 6.78866, 899.617, 247.117)
n_butane = Compound("n-Butane", 58.12, 6.80896, 935.86, 238.73)
propane = Compound("Propane", 44.10, 6.82973, 813.2, 248.0)
methanol = Compound("Methanol", 32.04, 8.08097, 1582.271, 239.726)
benzene = Compound("Benzene", 78.11, 6.90565, 1211.033, 220.790)
toluene = Compound("Toluene", 92.14, 6.95464, 1344.800, 219.482)

PAIRS = {
    "Ethanol/Water": (ethanol, water),
    "Isobutane/n-Butane": (isobutane, n_butane),
    "Propane/n-Butane": (propane, n_butane),
    "Methanol/Water": (methanol, water),
    "Benzene/Toluene": (benzene, toluene),
}
