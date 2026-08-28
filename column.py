import numpy as np

from mass_balance import overall_massbalance
from relative_vol import relative_vol
from thermodynamics import relative_volatility, compute_rmin
from stage_stepping import inverse_eqcurve, step_stages, find_pinch_point
from sizing import column_height, column_diameter
from economics import (
    condenser_duty,
    reboiler_duty,
    utility_costs,
    equipment_cost,
    annualized_capital_cost,
    total_annual_cost,
)
from plotting import plot_mccabe_thiele, plot_tac_vs_R
from compounds import ethanol, water


class DistillationColumn:
    def __init__(
        self,
        F=120,  # kmol/h
        zF=0.40,
        P=1,  # atm
        T=78,  # C
        q=1,
        xD=0.92,
        xB=0.15,
        Eo=0.75,
        tray_spacing=0.5,  # m
        light=ethanol,
        heavy=water,
    ):
        self.F = F
        self.zF = zF
        self.P = P
        self.T = T
        self.q = 1
        self.xD = xD
        self.xB = xB
        self.Eo = Eo
        self.tray_spacing = tray_spacing
        self.light = light
        self.heavy = heavy
        self.MW_eth = light.MW
        self.MW_wat = heavy.MW

        self.alfa = None
        self.Rmin = None
        self.y_feed_eq = None
        self.R_values = None
        self.TACs = []
        self.iterations = []
        self.idx_opt = None
        self.optimum = None

    def run(self):
        F = self.F
        zF = self.zF
        P = self.P
        T = self.T
        q = self.q
        xD = self.xD
        xB = self.xB
        Eo = self.Eo
        tray_spacing = self.tray_spacing
        MW_eth = self.MW_eth
        MW_wat = self.MW_wat

        # relative volatility
        alfa = relative_volatility(T, P, self.light, self.heavy)

        # Rmin
        Rmin, y_feed_eq = compute_rmin(alfa, zF, xD)

        print(f"Rmin: {Rmin:.4f}")

        self.alfa = alfa
        self.Rmin = Rmin
        self.y_feed_eq = y_feed_eq

        if Rmin == 0:
            R_values = np.linspace(0.05, 2.0, 1000)
        else:
            R_values = np.linspace(1.05 * Rmin, 2.0 * Rmin, 1000)

        TACs = []
        iterations = []

        for R in R_values:

            # mass balance
            B, D = overall_massbalance(F, zF, xD, xB)
            print(F, B, D)

            # relative volatility
            alfa = relative_vol(T, P, self.light, self.heavy)

            # eq curve
            x = np.linspace(0, 1, 100)
            y_eqcurve = (alfa * x) / (1 + (alfa - 1) * x)

            # diagonal
            y_d = x

            # rec line, kept only where it lies between the diagonal and the eq curve
            # ============ RECTIFYING LINE (General Form) ============
            # L = R*D, V = (R+1)*D
            L = R * D
            V = (R + 1) * D

            # Rectifying line: y = (L/V)*x + (D/V)*xD
            # But L/V = R/(R+1) and D/V = 1/(R+1)
            m_rec = L / V  # = R/(R+1)
            b_rec = D * xD / V  # = xD/(R+1)

            print(f"Rectifying line: y = {m_rec:.4f}x + {b_rec:.4f}")
            # Rectifying line (full range, but we'll mask it)
            y_rec = m_rec * x + b_rec
            # Mask: only where it's between diagonal and equilibrium curve

            # q-line: q=1 (saturated liquid feed) -> vertical at x=zF,
            # drawn from the diagonal up to the feed point on the rectifying line
            print(f"q-line: x = {zF}")
            y_feed_on_rec = m_rec * zF + b_rec
            x_q = [zF, zF]
            y_q = [zF, y_feed_on_rec]  # From diagonal to rectifying line

            # strip slope
            # ============ STRIPPING LINE (General Form) ============
            # L' = L + q*F
            # V' = V - (1-q)*F
            L_prime = L + q * F
            V_prime = V - (1 - q) * F

            # Stripping line: y = (L'/V')*x - (B/V')*xB
            m_strip = L_prime / V_prime
            b_strip = -B * xB / V_prime

            print(f"Stripping line: y = {m_strip:.4f}x + {b_strip:.4f}")
            # Stripping line (full range)
            y_strip = m_strip * x + b_strip

            # Mask: only where it's below equilibrium curve

            # stepping
            x_list, y_list = step_stages(xD, xB, zF, alfa, R, m_strip, b_strip)

            # Count theoretical stages correctly (subtract 1 for the starting point)
            N_theoretical = len(x_list) - 1
            N_actual = (N_theoretical / Eo) + 1
            print(f"N_actual: {N_actual:.0f}")

            print("N_theoretical:", N_theoretical)

            # Print starting point and each stage
            print(f"x0 = {xD:.6f}, y0 = {xD:.6f} (starting point)")
            for i in range(1, len(x_list)):
                print(f"x{i} = {x_list[i]:.6f}, y{i} = {y_list[i]:.6f}")

            x_arr = np.array(x_list)
            y_arr = np.array(y_list)
            feasible = (
                len(x_list) <= 500
                and np.all(x_arr >= -1e-6) and np.all(x_arr <= 1 + 1e-6)
                and np.all(y_arr >= -1e-6) and np.all(y_arr <= 1 + 1e-6)
            )

            # height of vessel
            H_vessel = column_height(N_actual, tray_spacing)

            print(f"Column height H_vessel = {H_vessel:.2f} m")

            # diameter of vessel
            V = (R + 1) * D
            Dc, A_col, MW_vap_avg = column_diameter(V, xD, MW_eth, MW_wat)

            print(f"Vapor flow V = {V:.2f} kmol/h")
            print(f"Column diameter Dc = {Dc:.3f} m")
            print(f"Column cross-sectional area A_col = {A_col:.3f} m^2")

            # condenser
            Qc = condenser_duty(V)

            print(f"Condenser duty Qc = {Qc:.3e} kJ/h")

            # reboiler
            Qr = reboiler_duty(Qc)

            print(f"Reboiler duty Qr = {Qr:.3e} kJ/h")

            # utility
            SteamYear, CoolingYear = utility_costs(Qr, Qc)

            print(f"Steam cost   = ${SteamYear:,.0f} /year")
            print(f"Cooling cost = ${CoolingYear:,.0f} /year")

            # equipment cost
            ShellCost, TrayCost, CondenserCost, ReboilerCost, PurchaseCost = equipment_cost(
                Dc, H_vessel, N_actual, Qc, Qr
            )

            print(f"Shell cost      = ${ShellCost:,.0f}")
            print(f"Tray cost        = ${TrayCost:,.0f}")
            print(f"Condenser cost   = ${CondenserCost:,.0f}")
            print(f"Reboiler cost    = ${ReboilerCost:,.0f}")
            print(f"Total purchase cost = ${PurchaseCost:,.0f}")

            # annual cost
            CRF, AnnualCapital = annualized_capital_cost(PurchaseCost)

            print(f"CRF = {CRF:.5f}")
            print(f"Annualized capital cost = ${AnnualCapital:,.0f} /year")

            # Total Annual Cost (TAC)
            TAC = total_annual_cost(AnnualCapital, SteamYear, CoolingYear)

            print(f"Total anual cost (TAC) = ${TAC:,.0f} /year")

            TACs.append(TAC if feasible else np.inf)

            iterations.append({
                "R": R,
                "B": B,
                "D": D,
                "alfa": alfa,
                "x": x,
                "y_eqcurve": y_eqcurve,
                "y_d": y_d,
                "y_rec": y_rec,
                "y_strip": y_strip,
                "x_q": x_q,
                "y_q": y_q,
                "m_rec": m_rec,
                "b_rec": b_rec,
                "m_strip": m_strip,
                "b_strip": b_strip,
                "L": L,
                "V": V,
                "L_prime": L_prime,
                "V_prime": V_prime,
                "x_list": x_list,
                "y_list": y_list,
                "N_theoretical": N_theoretical,
                "N_actual": N_actual,
                "H_vessel": H_vessel,
                "Dc": Dc,
                "A_col": A_col,
                "MW_vap_avg": MW_vap_avg,
                "Qc": Qc,
                "Qr": Qr,
                "SteamYear": SteamYear,
                "CoolingYear": CoolingYear,
                "ShellCost": ShellCost,
                "TrayCost": TrayCost,
                "CondenserCost": CondenserCost,
                "ReboilerCost": ReboilerCost,
                "PurchaseCost": PurchaseCost,
                "CRF": CRF,
                "AnnualCapital": AnnualCapital,
                "TAC": TAC,
                "feasible": feasible,
            })

        self.R_values = R_values
        self.TACs = TACs
        self.iterations = iterations

        if not any(it["feasible"] for it in iterations):
            raise ValueError("No feasible reflux ratio found in the search range.")

        self.idx_opt = int(np.argmin(TACs))
        self.optimum = iterations[self.idx_opt]

        # plotting
        plot_mccabe_thiele(x, y_strip, y_rec, y_eqcurve, y_d, xB, xD, x_q, y_q)

        print(R_values)
        print(TACs)

        plot_tac_vs_R(R_values, TACs)

        print(f"TAC for the most optimum R: ${min(TACs):.2f}")