from app import app
import os
from prometheus_flask_exporter import PrometheusMetrics
from app import app

metrics = PrometheusMetrics(app)
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
