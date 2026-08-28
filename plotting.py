import matplotlib

for backend in ("TkAgg", "Qt5Agg"):
    try:
        matplotlib.use(backend)
        break
    except Exception:
        continue

import matplotlib.pyplot as plt


def plot_mccabe_thiele(x, y_strip, y_rec, y_eqcurve, y_d, xB, xD, x_q, y_q):
    plt.plot(x, y_strip, label="strip line", color='black')
    plt.plot(x_q, y_q, 'g-', linewidth=2, label='q-line (q=1, vertical)')
    plt.plot(x, y_rec, label='rec line', color='orange')
    plt.axvline(x=xB, color='black', linestyle='--')
    plt.axvline(x=xD, color='black', linestyle='--')
    plt.plot(x, y_eqcurve, label='eq curve', color='red')
    plt.plot(x, y_d, label='diagonal', color='blue')
    y = 0
    plt.scatter(xD, 0, color='red', s=25)
    plt.scatter(xB, 0, color='red', s=25)

    plt.text(xD + 0.01, y, "xD", fontsize=12, fontweight='bold')
    plt.text(xB + 0.01, y, "xB", fontsize=12, fontweight='bold')

    # extra plot info
    plt.title('McCabe–Thiele')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()

    plt.show()


def plot_tac_vs_R(R_values, TACs):
    plt.plot(R_values, TACs)
    plt.xlabel("R")
    plt.ylabel("TAC")
    plt.show()