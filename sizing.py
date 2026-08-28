import numpy as np


def column_height(N_actual, tray_spacing, disengagement_height=2.0):
    H_vessel = N_actual * tray_spacing + disengagement_height
    return H_vessel


def column_diameter(V, xD, MW_eth, MW_wat, rho_v=1.2, u_vap=0.85):
    MW_vap_avg = xD * MW_eth + (1 - xD) * MW_wat  # kg/kmol
    m_dot_vap = V * MW_vap_avg  # kg/h
    m_dot_vap_s = m_dot_vap / 3600.0  # kg/s
    Q_vap = m_dot_vap_s / rho_v  # m3/s
    A_col = Q_vap / u_vap  # m2
    Dc = np.sqrt(4 * A_col / np.pi)  # m, column diameter
    return Dc, A_col, MW_vap_avg