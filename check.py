"""Run the appropriate DeskHive checks from any working directory."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IS_STARTER = (ROOT / 'M6-EXERCISES.md').exists()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    for flag in ('smoke', 'all', 'web', 'core', 'rules', 'm4', 'm5', 'm6-lab1', 'm6'):
        mode.add_argument('--' + flag, action='store_true')
    args = parser.parse_args()
    chosen = next((flag for flag in ('smoke', 'all', 'web', 'core', 'rules', 'm4', 'm5', 'm6-lab1', 'm6') if getattr(args, flag.replace('-', '_'))),
                  'm5' if IS_STARTER else 'all')
    if chosen == 'smoke' and not IS_STARTER:
        parser.error('--smoke is only for the untouched starter; use --all for the solution')
    jobs = {
        'smoke': [('deskhive-web', ['manage.py', 'test', 'spaces.smoke_tests', '-v', '2']),
                  ('deskhive-core', ['-m', 'unittest', '-v', 'smoke_tests'])],
        'web': [('deskhive-web', ['manage.py', 'test', 'spaces', 'bookings', '-v', '2'])],
        'core': [('deskhive-core', ['-m', 'unittest', 'discover', '-s', 'tests', '-v'])],
        'rules': [('deskhive-core', ['-m', 'unittest', '-v', 'tests.test_booking'])],
    }
    jobs['m4'] = [('deskhive-web', ['manage.py', 'test', 'spaces.tests', 'spaces.test_m4', 'bookings.tests', '-v', '2'])]
    jobs['m5'] = [('deskhive-web', ['manage.py', 'test', 'spaces', 'bookings', '-v', '2'])]
    jobs['m6-lab1'] = [('deskhive-web', ['manage.py', 'test', 'api_m6.tests.SerializerBasicsTests', '-v', '2'])]
    jobs['m6'] = [('deskhive-web', ['manage.py', 'test', 'api_m6.tests', '-v', '2'])]
    jobs['all'] = jobs['web'] + jobs['m6'] + jobs['core']
    failed = False
    for folder, command in jobs[chosen]:
        print(f"\nChecking {folder}: {' '.join(command)}", flush=True)
        result = subprocess.run([sys.executable, *command], cwd=ROOT / folder)
        failed = failed or result.returncode != 0
    if failed and IS_STARTER and chosen != 'smoke':
        print('Acceptance failures are expected until the starter exercises are completed.', flush=True)
    return int(failed)

if __name__ == '__main__':
    raise SystemExit(main())
