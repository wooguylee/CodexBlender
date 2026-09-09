"""Client must wait for transport retirement, not just a prematurely published result."""
from pathlib import Path
import sys
import tempfile
import threading
import time
from types import SimpleNamespace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'bridge'))
import client
from common import FileLock, is_locked, write_json


class CompletionTests(unittest.TestCase):
    def test_result_is_not_returned_before_worker_retires_request(self):
        original = client.ROOT, client.RUNTIME
        try:
            for action in ('scene', 'stop'):
                with self.subTest(action=action), tempfile.TemporaryDirectory() as temporary:
                    root = Path(temporary).resolve()
                    runtime = root / '.runtime'
                    client.ROOT, client.RUNTIME = root, runtime
                    folder = runtime / 'sessions' / 'testsession'
                    (folder / 'queue').mkdir(parents=True)
                    (folder / 'working').mkdir()
                    ready = threading.Event()
                    retired = threading.Event()
                    errors = []

                    def delayed_worker():
                        try:
                            with FileLock(runtime / 'bridge.lock'):
                                write_json(runtime / 'connection.json', {'session': 'testsession'})
                                ready.set()
                                deadline = time.monotonic() + 3
                                while not (jobs := list((folder / 'queue').glob('*.json'))):
                                    if time.monotonic() > deadline:
                                        raise TimeoutError('test client did not submit')
                                    time.sleep(.01)
                                job = jobs[0]
                                working = folder / 'working' / job.name
                                job.replace(working)
                                write_json(root / 'outputs/jobs' / job.stem / 'result.json', {'ok': True})
                                time.sleep(.5)
                                working.unlink()
                                retired.set()
                        except BaseException as error:
                            errors.append(error)

                    thread = threading.Thread(target=delayed_worker)
                    thread.start()
                    self.assertTrue(ready.wait(2))
                    try:
                        result = client.send(SimpleNamespace(command=action, timeout=3))
                        self.assertTrue(result['ok'])
                        self.assertTrue(retired.is_set(), 'client returned before the prior job retired')
                        if action == 'stop':
                            self.assertFalse(is_locked(runtime / 'bridge.lock'))
                    finally:
                        thread.join(4)
                    self.assertFalse(errors)
        finally:
            client.ROOT, client.RUNTIME = original


if __name__ == '__main__':
    unittest.main()
