def condenser_duty(V, lambda_latent=35000):
    Qc = V * lambda_latent  # kJ/h
    return Qc


def reboiler_duty(Qc):
    Qr = Qc
    return Qr


def utility_costs(Qr, Qc, hours=8000, steam_cost=12, cw_cost=0.35):
    # Convert kJ/h -> GJ/year
    Qr_GJ_year = Qr * hours / 1e6  # GJ/year
    Qc_GJ_year = Qc * hours / 1e6  # GJ/year

    SteamYear = Qr_GJ_year * steam_cost  # $/year
    CoolingYear = Qc_GJ_year * cw_cost  # $/year
    return SteamYear, CoolingYear


def equipment_cost(Dc, H_vessel, N_actual, Qc, Qr):
    a_shell, b_shell, c_shell = 8000, 1.1, 0.8
    ShellCost = a_shell * Dc ** b_shell * H_vessel ** c_shell  # $

    tray_unit_cost = 120  # $ per actual tray
    TrayCost = tray_unit_cost * N_actual ** 2.6  # $

    # Condenser and reboiler cost placeholders, scaled on duty (kJ/h -> kW)
    Qc_kW = Qc / 3600.0
    Qr_kW = Qr / 3600.0

    CondenserCost = 1200 * Qc_kW ** 0.65  # $, illustrative power-law form
    ReboilerCost = 1400 * Qr_kW ** 0.65  # $, illustrative power-law form

    PurchaseCost = ShellCost + TrayCost + CondenserCost + ReboilerCost

    return ShellCost, TrayCost, CondenserCost, ReboilerCost, PurchaseCost


def annualized_capital_cost(PurchaseCost, i=0.10, n=10):
    CRF = i * (1 + i) ** n / ((1 + i) ** n - 1)
    AnnualCapital = PurchaseCost * CRF  # $/year
    return CRF, AnnualCapital


def total_annual_cost(AnnualCapital, SteamYear, CoolingYear):
    TAC = AnnualCapital + SteamYear + CoolingYear  # $/year
    return TAC