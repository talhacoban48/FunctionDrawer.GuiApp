from pathlib import Path
from sympy import symbols
from sympy.parsing.sympy_parser import (
    parse_expr, standard_transformations,
    implicit_multiplication_application, convert_xor,
)

# Proje kök dizini ve asset yolu
BASE_DIR   = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / 'assets'


def asset(name: str) -> str:
    return str(ASSETS_DIR / name)


# Sembolik değişken
X = symbols('x')

# Sympy parser dönüşümleri (doğal notasyon: 2x, x^2, ...)
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def parse_formula(text: str):
    """Doğal matematik notasyonunu sympy ifadesine çevirir."""
    return parse_expr(text, transformations=TRANSFORMATIONS, local_dict={'x': X})


# Fonksiyon renk paleti
COLORS = [
    'steelblue', 'darkorange', 'seagreen', '#cc3333',
    "#19d332", '#e67e22', '#1abc9c', "#b01ee9",
]
