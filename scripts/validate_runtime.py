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
port = int(os.getenv('API_PORT', '18000'))
base_url = f'http://127.0.0.1:{port}'
report_path = ROOT / 'reports/runtime.json'
report = json.loads(report_path.read_text(encoding='utf-8')) if report_path.exists() else {}
with (ROOT / 'reports/runtime-server.log').open('w', encoding='utf-8') as logfile:
    server = None if os.getenv('EXTERNAL_API') == '1' else subprocess.Popen([sys.executable, '-m', 'uvicorn', 'api.main:app', '--host', '127.0.0.1', '--port', str(port)], cwd=ROOT, stdout=logfile, stderr=logfile, creationflags=flags)
    try:
        for _ in range(60):
            if server is not None and server.poll() is not None:
                raise RuntimeError('API failed to start; see reports/runtime-server.log')
            try:
                with urllib.request.urlopen(base_url + '/health', timeout=2) as response:
                    report['health'] = json.load(response)
                break
            except OSError:
                time.sleep(1)
        else:
            raise RuntimeError('API readiness timeout')
        payload = json.dumps(dict(age=35, anciennete=5, revenu=450000, nb_reclamations=2, montant_mensuel=25000, retards_paiement=2)).encode()
        request = urllib.request.Request(base_url + '/predict', data=payload, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(request, timeout=10) as response:
            report['prediction'] = json.load(response)
        env = {**os.environ, 'RUN_E2E': '1', 'API_URL': base_url}
        if os.getenv('SKIP_SELENIUM') != '1':
            result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/test_selenium.py', '-q'], env=env, cwd=ROOT, capture_output=True, text=True, timeout=240, creationflags=flags)
            report['selenium'] = {'exit_code': result.returncode, 'output': result.stdout + result.stderr}
        jmeter = ROOT / 'tools/apache-jmeter-5.6.3/bin/ApacheJMeter.jar'
        if jmeter.exists():
            load = ROOT / 'reports/load'
            load.mkdir(parents=True, exist_ok=True)
            if not isinstance(report.get('load'), dict):
                report['load'] = {}
            users_to_run = [int(value) for value in os.getenv('LOAD_USERS', '100,500,1000').split(',')]
            repeat = os.getenv('REPEAT_LOAD') == '1'
            label = os.getenv('RUN_LABEL', 'repeat' if repeat else '')
            if label and not label.replace('-', '').isalnum():
                raise ValueError('RUN_LABEL must contain only letters, digits and hyphens')
            for users in users_to_run:
                tag = f'{users}-{label}' if label else str(users)
                if repeat and str(users) in report['load']:
                    previous = report['load'][str(users)]
                    report.setdefault('previous_runs', {})[previous.get('source', f'{users}-legacy')] = previous
                output = load / f'{tag}.jtl'
                if output.exists():
                    raise RuntimeError(f'Existing output: {output}')
                try:
                    result = subprocess.run(['java', '-jar', str(jmeter), '-n', '-t', str(ROOT / 'tests/load/churn.jmx'), f'-Jusers={users}', f'-Jport={port}', '-Jramp=10', '-Jloops=10', '-l', str(output), '-j', str(load / f'{tag}.log'), '-e', '-o', str(load / tag)], cwd=ROOT, capture_output=True, text=True, timeout=900, creationflags=flags)
                except subprocess.TimeoutExpired:
                    report['load'][str(users)] = {'valid_measurement': False, 'error': 'Execution interrupted or exceeded 900 seconds', 'source': str(output.relative_to(ROOT))}
                    continue
                if result.returncode:
                    report['load'][str(users)] = {'exit_code': result.returncode, 'output': result.stdout + result.stderr}
                    continue
                with output.open(encoding='utf-8') as stream:
                    rows = list(csv.DictReader(stream))
                durations = sorted(float(row['elapsed']) for row in rows)
                span = (max(float(row['timeStamp']) + float(row['elapsed']) for row in rows) - min(float(row['timeStamp']) for row in rows)) / 1000
                report['load'][str(users)] = {'requests': len(rows), 'mean_ms': statistics.mean(durations), 'median_ms': statistics.median(durations), 'p90_ms': durations[int(.9 * (len(rows) - 1))], 'p95_ms': durations[int(.95 * (len(rows) - 1))], 'max_ms': max(durations), 'valid_measurement': max(durations) <= 60000, 'requests_per_second': len(rows) / span, 'error_percent': 100 * sum(row['success'] != 'true' for row in rows) / len(rows), 'source': str(output.relative_to(ROOT))}
                (ROOT / 'reports/runtime.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        else:
            report['load'] = 'JMeter unavailable'
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
        (ROOT / 'reports/runtime.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
