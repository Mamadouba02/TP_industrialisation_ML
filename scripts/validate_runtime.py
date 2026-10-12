"""Run real HTTP, Selenium and optional JMeter checks against a temporary API."""
import csv
import json
import os
from pathlib import Path
import statistics
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
report_path = ROOT / 'reports/runtime.json'
report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
with (ROOT / 'reports/runtime-server.log').open('w', encoding='utf-8') as logfile:
    server = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', '18000'], cwd=ROOT, stdout=logfile, stderr=logfile, creationflags=flags)
    try:
        for _ in range(60):
            if server.poll() is not None:
                raise RuntimeError('API failed to start; see reports/runtime-server.log')
            try:
                with urllib.request.urlopen('http://127.0.0.1:18000/health', timeout=2) as response:
                    report['health'] = json.load(response)
                break
            except OSError:
                time.sleep(1)
        else:
            raise RuntimeError('API readiness timeout')
        payload = json.dumps(dict(age=35, anciennete=5, revenu=450000, nb_reclamations=2, montant_mensuel=25000, retards_paiement=2)).encode()
        request = urllib.request.Request('http://127.0.0.1:18000/predict', data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=10) as response:
            report['prediction'] = json.load(response)
        env = {**os.environ, 'RUN_E2E': '1', 'API_URL': 'http://127.0.0.1:18000'}
        if os.getenv('SKIP_SELENIUM') != '1':
            result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_selenium.py', '-q'], env=env, cwd=ROOT, capture_output=True, text=True, timeout=240, creationflags=flags)
            report['selenium'] = {'exit_code': result.returncode, 'output': result.stdout + result.stderr}
        jmeter = ROOT / 'tools/apache-jmeter-5.6.3/bin/ApacheJMeter.jar'
        if jmeter.exists():
            load = ROOT / 'reports/load'
            load.mkdir(parents=True, exist_ok=True)
            report['load'] = {}
            for users in [100, 500, 1000]:
                output = load / f'{users}.jtl'
                if output.exists():
                    raise RuntimeError(f'Existing output: {output}')
                result = subprocess.run(['java', '-jar', str(jmeter), '-n', '-t', str(ROOT / 'tests/load/churn.jmx'), f'-Jusers={users}', '-Jport=18000', '-Jramp=10', '-Jloops=10', '-l', str(output), '-j', str(load / f'{users}.log'), '-e', '-o', str(load / str(users))], cwd=ROOT, capture_output=True, text=True, timeout=900, creationflags=flags)
                if result.returncode:
                    report['load'][str(users)] = {'exit_code': result.returncode, 'output': result.stdout + result.stderr}
                    continue
                with output.open(encoding='utf-8') as stream:
                    rows = list(csv.DictReader(stream))
                durations = sorted(float(row['elapsed']) for row in rows)
                span = (max(float(row['timeStamp']) + float(row['elapsed']) for row in rows) - min(float(row['timeStamp']) for row in rows)) / 1000
                report['load'][str(users)] = {'requests': len(rows), 'mean_ms': statistics.mean(durations), 'median_ms': statistics.median(durations), 'p90_ms': durations[int(.9 * (len(rows) - 1))], 'p95_ms': durations[int(.95 * (len(rows) - 1))], 'requests_per_second': len(rows) / span, 'error_percent': 100 * sum(row['success'] != 'true' for row in rows) / len(rows)}
                (ROOT / 'reports/runtime.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        else:
            report['load'] = 'JMeter unavailable'
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        (ROOT / 'reports/runtime.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
