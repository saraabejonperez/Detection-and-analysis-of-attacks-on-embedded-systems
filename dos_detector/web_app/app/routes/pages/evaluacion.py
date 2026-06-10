import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
import pytz
from flask import Blueprint, render_template, request, flash, session, current_app
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from ...models import db, Modelo


evaluacion_bp = Blueprint("evaluacion", __name__)


@evaluacion_bp.route("/evaluacion", methods=["GET", "POST"])
def index():
    """
    Evaluate a selected machine learning model using a standard test dataset.
    
    On a GET request: display the evaluation interface.
    On a POST request: identify the selected model, perform inference 
    on a pre-configured test dataset on the server, and return the statistics to the template.

    :return: The rendered HTML template displaying the model selection form 
             and, if a valid POST request was processed, the evaluation metrics.
    :rtype: str
    """
    if session.get('guest'):
        modelos = session.get('guest_models', [])
    else:
        user_id = session.get('user_id')
        modelos = Modelo.query.filter_by(usuario_id=user_id).all() if user_id else []

    resultados = None

    if request.method == "POST":
        model_id = request.form.get("model_id")
        
        if model_id is None or model_id == "":
            flash("Por favor, selecciona un modelo de la lista.", "error")
            return render_template("evaluacion.html", modelos=modelos, resultados=resultados)

        ruta_modelo = None
        ruta_features = None
        
        if session.get('guest'):
            try:
                idx = int(model_id)
                ruta_modelo = modelos[idx]['ruta_archivo']
                ruta_features = modelos[idx]['ruta_features']
            except:
                flash("Modelo temporal no encontrado.", "error")
        else:
            modelo_db = Modelo.query.filter_by(id=model_id, usuario_id=session.get('user_id')).first()
            if modelo_db:
                ruta_modelo = modelo_db.ruta_archivo
                if modelo_db.archivos_config:
                    ruta_features = modelo_db.archivos_config[0].ruta_archivo
                modelo_db.fecha_ultimo_uso = datetime.now(pytz.timezone('Europe/Madrid'))
                db.session.commit()

        if not ruta_modelo or not os.path.exists(ruta_modelo):
            flash("El archivo del modelo no se encuentra en el servidor.", "error")
            return render_template("evaluacion.html", modelos=modelos, resultados=resultados)
        
        if not ruta_features or not os.path.exists(ruta_features):
            flash("Falta el archivo de configuración (features.npy) para este modelo.", "error")
            return render_template("evaluacion.html", modelos=modelos, resultados=resultados)

        try:
            features = np.load(ruta_features, allow_pickle=True)
            
            model = joblib.load(ruta_modelo)

            test_data_path = os.path.join(current_app.root_path, '..', 'data', 'test_data.csv')
            if not os.path.exists(test_data_path):
                flash("Fallo interno: Dataset de evaluación no configurado en el servidor.", "error")
                return render_template("evaluacion.html", modelos=modelos, resultados=resultados)

            df_test = pd.read_csv(test_data_path)
            X_test = df_test[features]
            y_test = df_test['label']

            y_pred = model.predict(X_test)
            
            cm = confusion_matrix(y_test, y_pred)
            tn, fp, fn, tp = cm.ravel().tolist()

            resultados = {
                "accuracy": round(accuracy_score(y_test, y_pred) * 100, 2),
                "precision": round(precision_score(y_test, y_pred, zero_division=0) * 100, 2),
                "recall": round(recall_score(y_test, y_pred, zero_division=0) * 100, 2),
                "f1": round(f1_score(y_test, y_pred, zero_division=0) * 100, 2),
                "cm": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
                "total_samples": len(y_test)
            }
            flash("Evaluación completada.", "success")
            
        except Exception as e:
            flash(f"Error al evaluar el modelo: {str(e)}", "error")

    return render_template("evaluacion.html", modelos=modelos, resultados=resultados)