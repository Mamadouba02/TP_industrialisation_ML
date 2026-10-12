"""Build reviewable notebook, Grafana dashboard and JMeter plan."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]

cells = [
    {'cell_type': 'markdown', 'metadata': {}, 'source': ['# Exploration du churn\n', 'Données synthétiques pédagogiques ; exécuter les cellules depuis la racine ou notebooks.']},
    {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': ['from pathlib import Path\n', 'import pandas as pd\n', 'import matplotlib.pyplot as plt\n', 'import seaborn as sns\n', "root = Path.cwd() if (Path.cwd() / 'data/raw/churn.csv').exists() else Path.cwd().parent\n", "df = pd.read_csv(root / 'data/raw/churn.csv')\n", 'df.head()']},
    {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': ['print(df.shape)\n', 'print(df.dtypes)\n', 'print(df.isna().sum())\n', 'df.describe()']},
    {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': ["print(df.churn.value_counts(normalize=True))\n", "sns.countplot(data=df, x='churn')\n", 'plt.show()']},
    {'cell_type': 'code', 'metadata': {}, 'execution_count': None, 'outputs': [], 'source': ['plt.figure(figsize=(10, 6))\n', "sns.heatmap(df.corr(), annot=True, fmt='.2f')\n", 'plt.show()']},
    {'cell_type': 'markdown', 'metadata': {}, 'source': ['## Interprétation\n', 'La formule génératrice favorise le churn quand le montant et les retards augmentent et quand l’ancienneté diminue. Les corrélations ne prouvent pas une causalité. Les résultats sur ce jeu synthétique ne garantissent pas une généralisation sur des clients réels.']},
]
for index, cell in enumerate(cells):
    cell['id'] = f'churn-{index}'
(ROOT / 'notebooks/exploration.ipynb').write_text(json.dumps({'cells': cells, 'metadata': {'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'}}, 'nbformat': 4, 'nbformat_minor': 5}, ensure_ascii=False, indent=2), encoding='utf-8')
queries = [
    ('Requêtes par seconde', 'sum(rate(http_requests_total[5m]))'),
    ('Temps de réponse p95 (s)', 'histogram_quantile(0.95, sum by (le) (rate(http_request_duration_seconds_bucket[5m])))'),
    ('Erreurs HTTP par seconde', 'sum(rate(http_requests_total{status=~"5.."}[5m]))'),
    ('Taux d’erreur HTTP', 'sum(rate(http_requests_total{status=~"5.."}[5m])) / clamp_min(sum(rate(http_requests_total[5m])), 0.000001)'),
    ('Nombre de prédictions', 'sum(churn_predictions_total)'),
]
panels = [{'id': i + 1, 'title': title, 'type': 'timeseries', 'datasource': {'type': 'prometheus', 'uid': 'prometheus'}, 'gridPos': {'x': (i % 2) * 12, 'y': (i // 2) * 8, 'w': 12, 'h': 8}, 'targets': [{'refId': 'A', 'expr': query}]} for i, (title, query) in enumerate(queries)]
dashboard = ROOT / 'monitoring/grafana/dashboards/churn.json'
dashboard.parent.mkdir(parents=True, exist_ok=True)
dashboard.write_text(json.dumps({'uid': 'churn-api', 'title': 'ML Churn API', 'schemaVersion': 39, 'version': 1, 'refresh': '5s', 'time': {'from': 'now-30m', 'to': 'now'}, 'panels': panels}, ensure_ascii=False, indent=2), encoding='utf-8')
body = json.dumps(dict(age=35, anciennete=5, revenu=450000, nb_reclamations=2, montant_mensuel=25000, retards_paiement=2))
plan = '''<?xml version="1.0" encoding="UTF-8"?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3"><hashTree>
<TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Churn API load" enabled="true"><boolProp name="TestPlan.functional_mode">false</boolProp><boolProp name="TestPlan.serialize_threadgroups">false</boolProp><elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments"><collectionProp name="Arguments.arguments"/></elementProp></TestPlan><hashTree>
<ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Concurrent clients" enabled="true"><stringProp name="ThreadGroup.on_sample_error">continue</stringProp><elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController"><boolProp name="LoopController.continue_forever">false</boolProp><stringProp name="LoopController.loops">${__P(loops,10)}</stringProp></elementProp><stringProp name="ThreadGroup.num_threads">${__P(users,100)}</stringProp><stringProp name="ThreadGroup.ramp_time">${__P(ramp,10)}</stringProp><boolProp name="ThreadGroup.scheduler">false</boolProp></ThreadGroup><hashTree>
<HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="POST predict" enabled="true"><elementProp name="HTTPsampler.Arguments" elementType="Arguments"><collectionProp name="Arguments.arguments"><elementProp name="" elementType="HTTPArgument"><boolProp name="HTTPArgument.always_encode">false</boolProp><stringProp name="Argument.value">BODY</stringProp><stringProp name="Argument.metadata">=</stringProp></elementProp></collectionProp></elementProp><stringProp name="HTTPSampler.domain">${__P(host,localhost)}</stringProp><stringProp name="HTTPSampler.port">${__P(port,8000)}</stringProp><stringProp name="HTTPSampler.protocol">http</stringProp><stringProp name="HTTPSampler.path">/predict</stringProp><stringProp name="HTTPSampler.method">POST</stringProp><boolProp name="HTTPSampler.postBodyRaw">true</boolProp><boolProp name="HTTPSampler.use_keepalive">true</boolProp><stringProp name="HTTPSampler.connect_timeout">5000</stringProp><stringProp name="HTTPSampler.response_timeout">30000</stringProp></HTTPSamplerProxy><hashTree>
<HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="JSON header" enabled="true"><collectionProp name="HeaderManager.headers"><elementProp name="" elementType="Header"><stringProp name="Header.name">Content-Type</stringProp><stringProp name="Header.value">application/json</stringProp></elementProp></collectionProp></HeaderManager><hashTree/>
<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="HTTP 200" enabled="true"><collectionProp name="Asserion.test_strings"><stringProp name="0">200</stringProp></collectionProp><stringProp name="Assertion.test_field">Assertion.response_code</stringProp><intProp name="Assertion.test_type">8</intProp><boolProp name="Assertion.assume_success">false</boolProp></ResponseAssertion><hashTree/>
<ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Prediction result" enabled="true"><collectionProp name="Asserion.test_strings"><stringProp name="0">"prediction"</stringProp></collectionProp><stringProp name="Assertion.test_field">Assertion.response_data</stringProp><intProp name="Assertion.test_type">2</intProp><boolProp name="Assertion.assume_success">false</boolProp></ResponseAssertion><hashTree/>
</hashTree></hashTree></hashTree></hashTree></jmeterTestPlan>'''.replace('BODY', escape(body))
load = ROOT / 'tests/load/churn.jmx'
load.parent.mkdir(parents=True, exist_ok=True)
load.write_text(plan, encoding='utf-8')
for folder in ['frontend', 'reports/load']:
    (ROOT / folder).mkdir(parents=True, exist_ok=True)
