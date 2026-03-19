import matplotlib.pyplot as plt
import numpy as np

min = -10
max = 10
step = 0.01

def visualize_function(func):

    x_inputs = np.arange(min, max + step, step)

    x_values = []
    y_values = []

    for x in x_inputs:
        try:
            x = np.round(x, 4)
            y = func(x)
            y = np.round(y, 4)

            x_values.append(x)
            y_values.append(y)
            print(x, y)
        except:
            pass

    
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, linestyle='-', linewidth=1, markersize=1)
    
    plt.axhline(y=0, color='red', linewidth=0.5, label='y=0')
    plt.axvline(x=0, color='red', linewidth=0.5, label='x=0')
    
    plt.grid(True, alpha=0.3)
    
    plt.xlabel('x değeri', fontsize=12)
    plt.ylabel('f(x) değeri', fontsize=12)
    plt.title(f'Fonksiyon Grafiği ({np.round(np.min(x_inputs))} ile {np.round(np.max(x_inputs))} arası)', fontsize=14, fontweight='bold')
    
    plt.legend()
    
    plt.tight_layout()
    plt.show()


def fonksiyon(x):
    return (np.sin(4*x) - 2*np.sin(2*x)) / x**3

# Visualize et
visualize_function(fonksiyon)