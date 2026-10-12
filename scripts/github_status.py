"""Inspect this repository's CI using existing Git authentication, never printing tokens."""
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

BASE = 'https://api.github.com/repos/Mamadouba02/TP_industrialisation_ML'
headers = {'User-Agent': 'churn-tp-validation', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
credentials = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', capture_output=True, text=True, timeout=20, env={**os.environ, 'GIT_TERMINAL_PROMPT': '0', 'GCM_INTERACTIVE': 'never'})
if credentials.returncode == 0:
    fields = dict(line.split('=', 1) for line in credentials.stdout.splitlines() if '=' in line)
    if fields.get('password'):
        headers['Authorization'] = 'Bearer ' + fields['password']
    fields.clear()
del credentials

if '--dispatch' in sys.argv:
    request = urllib.request.Request(BASE + '/actions/workflows/ci.yml/dispatches', data=json.dumps({'ref': 'main'}).encode(), headers={**headers, 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            print(json.dumps({'dispatch_status': response.status}))
    except urllib.error.HTTPError as exc:
        message = json.loads(exc.read()).get('message', 'Dispatch failed')
        print(json.dumps({'dispatch_status': exc.code, 'message': message}))
    except OSError:
        print(json.dumps({'dispatch_error': 'Network unavailable'}))


def get(path):
    try:
        with urllib.request.urlopen(urllib.request.Request(BASE + path, headers=headers), timeout=15) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        return {'error_status': exc.code}
    except OSError:
        return {'error': 'Network unavailable'}


workflows = get('/actions/workflows')
permissions = get('/actions/permissions')
contents = get('/contents/.github/workflows/ci.yml')
runs = get('/actions/runs?per_page=5')
jobs = []
if '--jobs' in sys.argv and runs.get('workflow_runs'):
    details = get(f"/actions/runs/{int(runs['workflow_runs'][0]['id'])}/jobs")
    jobs = [{'id': job.get('id'), 'status': job.get('status'), 'conclusion': job.get('conclusion'), 'steps': [{key: step.get(key) for key in ('name', 'status', 'conclusion')} for step in job.get('steps', [])]} for job in details.get('jobs', [])]
print(json.dumps({'workflows': workflows, 'permissions': permissions, 'workflow_file': {key: contents.get(key) for key in ('path', 'sha', 'error_status', 'error')}, 'runs': [{key: run.get(key) for key in ('id', 'status', 'conclusion', 'head_branch', 'html_url')} for run in runs.get('workflow_runs', [])], 'runs_error': runs.get('error_status', runs.get('error')), 'jobs': jobs}, indent=2))
