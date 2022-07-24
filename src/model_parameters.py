
from dataclasses import dataclass
from scipy.constants import epsilon_0, elementary_charge, Boltzmann, Avogadro
import numpy as np
import pandas as pd
from dacite import from_dict
from scipy import interpolate

# from helper_functions import read_render_markdown_file

@dataclass
class Fluid:
    name: str
    symbol: str
    component: list[str]
    valence: np.ndarray
    temperature: float
    concentration: np.ndarray
    epsilon_r: float
    n_component: int
    n_pair: int
    index: int


fluid_parameters = dict({"kcl": dict({"name": "Potassium Chloride", "component": ["K", "Cl"], "valence": np.array([
    1.0, -1.0]), "temperature": 1075.0, "concentration": np.array([19.265, 19.265]),
    "epsilon_r": 1.0, "index": 1})})

fluid_parameters["h2o"] = dict({"name": "Liquid water", "component": ["H", "2O"], "valence": np.array([
    1.0, -1.0]), "temperature": 298.0, "concentration": np.array([1.0, 1.0]),
    "epsilon_r": 1.0, "index": 2})

fluid_parameters["2_2"] = dict({"name": "2-2 Aqueous electrolyte", "component": ["+2", "-2"], "valence": np.array([
    2.0, -2.0]), "temperature": 298.0, "concentration": np.array([1.0, 1.0]),
    "epsilon_r": 78.3, "index": 3})


def set_fluid_parameters(symbol):
    symbol = symbol.lower()
    if symbol not in fluid_parameters:
        return None
    parameters = fluid_parameters[symbol]
    parameters["symbol"] = "".join(parameters["component"])
    n_component = parameters["n_component"] = len(parameters["component"])
    parameters["n_pair"] = int((n_component+1) * (n_component) / 2)
    return from_dict(data_class=Fluid, data=parameters)


def fluid_specific_parameters(symbol):
    if symbol == "kcl":
        other_params = dict({"kcl": dict({"n_outer_shell": np.array([8., 8.]), "alpha": 1.0 / 0.337,
                                          "b": 0.338e-19, "sigma": [1.463, 1.585],
                                          "cap_c": np.array([24.3, 48.0, 124.5]) * 1e-19,
                                          "cap_d": np.array([24.0, 73.0, 250.0]) * 1e-19})})

    return other_params


def calc_beta(temperature):
    return 1.0 / (Boltzmann * temperature)


def calc_epsilon(epsilon_r):
    # units same as $\epsilon_0$ (need to allow for distances in angstrom)
    return 4.0 * np.pi * epsilon_r * epsilon_0


def calc_l_index(i, j):
    return i + j


def calc_beta_pauling(valence, n_outer_shell, n_component, n_pair):
    beta_pauling = np.zeros(n_pair)
    for i in range(n_component):
        for j in range(i, n_component):
            l = calc_l_index(i, j)
            beta_pauling[l] = 1.0 + valence[i] / \
                n_outer_shell[i] + valence[j] / n_outer_shell[j]
    return beta_pauling


def calc_cap_b(beta_pauling, b, alpha, sigma, n_component, n_pair):
    cap_b = np.zeros(n_pair)
    for i in range(n_component):
        for j in range(i, n_component):
            l = calc_l_index(i, j)
            cap_b[l] = beta_pauling[l] * b * np.exp(alpha * (sigma[i] + sigma[j]))
    return cap_b


def calc_charge(valence):
    return valence * elementary_charge


def calc_u(charge, cap_b, alpha, cap_c, cap_d, n_point, n_component, n_pair, epsilon, r):
    u = np.zeros((n_point, n_pair))
    for i in range(n_component):
        for j in range(i, n_component):
            l = calc_l_index(i, j)
            u[1:, l] = (charge[i] * charge[j]) / (r[1:] * 1e-10 * epsilon) + cap_c[l] / \
                r[1:]**6 + cap_d[l]/r[1:]**8 + \
                cap_b[l] * np.exp(-alpha * r[1:])
            u[0, l] = u[1, l]
    return u


def calc_rho(concentration):
    return np.array(concentration) / 1.0e27 * Avogadro


def calc_kappa(beta, charge, rho, epsilon):
    return np.sqrt(4.0 * np.pi * beta / epsilon * 1e10 *
    sum(np.multiply(charge**2, rho)))


def calc_phiw(z, n_component, phiw):
    capital_a = 16.274e-19 # joules
    wall_d = 2.97  # inverse Angstrom
    for i in range(n_component):
        phiw[:, i] = np.exp(-wall_d * z) * capital_a * (wall_d * z + 2)
    return phiw

#TODO: Fix up choice of c(r)
# Read in some c(r) -- currently LJ fluid (assuming c_short ~= c_LJ(r))

def interpolate_cr(r_in, cr_in, n_point, n_pair, z):
    cr = np.zeros((n_point, n_pair))
    for l in range(n_pair):
        f = interpolate.interp1d(r_in, cr_in[:, l])
        r = z
        cr[:, l] = f(r)
    return cr, r


def load_and_intepolate_cr(cr_path, n_point, n_pair, z):
    # CR_PATH = "../pyOZ_bulk_fluid/tests/lj/nrcg-cr.dat.orig"
    cr_df = pd.read_csv(cr_path, header=None, delim_whitespace=True)
    cr_df.set_index(0, inplace=True)
    r = cr_df.index.to_numpy()
    cr = cr_df.to_numpy()
    return interpolate_cr(r, cr, n_point, n_pair, z)