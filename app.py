from flask import Flask, request, render_template
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def prever():
    if request.method == 'POST':
        glicose = float(request.form.get('glicose'))
        hora_do_dia = request.form.get('hora_do_dia')
        hora, minuto = map(int, hora_do_dia.split(':'))
        hora_do_dia = hora + minuto / 60

        df = pd.read_csv(r"D:\nilza.csv", sep=';')
        df = df.replace(',', '.', regex=True)
        df['hora_do_dia'] = pd.to_datetime(df['hora_do_dia'], format='%H:%M', errors='coerce').dt.hour + pd.to_datetime(df['hora_do_dia'], format='%H:%M', errors='coerce').dt.minute / 60
        df.dropna(subset=['insulina'], inplace=True)

        if len(df) >= 2:
            df = df.sort_values(by='hora_do_dia')
            df['fator'] = df['glicose'].diff().fillna(0)
            X = df[['glicose', 'hora_do_dia', 'fator']]
            y = df['insulina']
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            ultima_glicose = df.iloc[-1]['glicose']
            fator = glicose - ultima_glicose

            if (glicose < 90 or glicose > 150) or (fator > 30):
                insulina_prevista = model.predict([[glicose, hora_do_dia, fator]])
                resultado = f'A insulina prevista é {insulina_prevista[0]}'
            else:
                resultado = "A glicose está dentro do intervalo seguro (90-150) e o fator de glicose é baixo."
        else:
            resultado = "Há menos de duas amostras no conjunto de dados. Por favor, adicione mais dados para continuar."

        return render_template('index.html', resultado=resultado)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
