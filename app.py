from flask import Flask, render_template, request, flash
import math
import matplotlib
matplotlib.use('Agg')  # Para evitar erros no servidor
import matplotlib.pyplot as plt
import io
import base64
import numpy as np

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'

def gerar_diagrama_tresca(sigma_e):
    fig, ax = plt.subplots(figsize=(8, 8))

    # Eixos
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)

    # --- Tresca (hexágono) com linha tracejada ---
    t = sigma_e
    tresca_x = [ t,  t,   0,  -t, -t,   0,  t ]
    tresca_y = [ 0,  t,   t,   0, -t,  -t,  0 ]
    ax.plot(tresca_x, tresca_y, color='mediumturquoise', linestyle='--', linewidth=2, label='Tresca')

    a = np.sqrt(2) * sigma_e
    b = np.sqrt(2/3) * sigma_e
    alpha = np.linspace(0, 2*np.pi, 360)
    theta = np.pi / 4

    x = (a * np.cos(alpha) * np.cos(theta)) - (b * np.sin(alpha) * np.sin(theta))
    y = (a * np.cos(alpha) * np.sin(theta)) + (b * np.sin(alpha) * np.cos(theta))

    ax.plot(x, y, color='deeppink', linewidth=2, label='Von Mises')
    ax.fill(x, y, color='deeppink', alpha=0.2)
    

    # Estética
    ax.set_title("Critérios de Tresca e Von Mises")
    ax.set_xlabel("σA (MPa)")
    ax.set_ylabel("σB (MPa)")
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    limite = 1.2 * sigma_e
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)

    # Exportar imagem
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()

    return plot_url


@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    plot_url = None
    
    if request.method == 'POST':
        try:
            sigma_x = float(request.form['sigma_x'])
            sigma_y = float(request.form['sigma_y'])
            tau_xy = float(request.form['tau_xy'])
            ten_esc = float(request.form['ten_e'])

            sigma_med = (sigma_x + sigma_y) / 2
            R = math.sqrt(((sigma_x - sigma_y) / 2) ** 2 + tau_xy ** 2)
            sigma_max = sigma_med + R
            sigma_min = sigma_med - R
            tau_max = R
            tau_e = ten_esc / 2
            cst = tau_e / tau_max
            csv = math.sqrt((ten_esc ** 2) / ((sigma_max ** 2) - (sigma_max * sigma_min) + (sigma_min ** 2)))

            sigma_e = sigma_max  # Utilizando σ_max como referência para o diagrama

            resultado = {
                'R': round(R, 2),
                'sigma_med': round(sigma_med, 2),
                'sigma_max': round(sigma_max, 2),
                'sigma_min': round(sigma_min, 2),
                'tau_max': round(tau_max, 2),
                'tau_e': round(tau_e, 2),
                'cst': round(cst, 2),
                'csv': round(csv, 2)
            }
            
            # Gerando o diagrama de Tresca com base nos pontos fornecidos
            plot_url = gerar_diagrama_tresca(sigma_e)
        except ValueError:
            flash('Erro: Insira valores numéricos válidos.', 'error')
    
    return render_template("index.html", resultado=resultado, plot_url=plot_url)

if __name__ == '__main__':
    import os

port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)