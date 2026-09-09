import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'bridge'))


class CommonTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('common'), 'Project transport is not implemented')
        import common
        self.common = common
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()

    def test_paths_cannot_escape_project(self):
        for path in ('../outside.blend', str(self.root.parent / 'outside.blend')):
            with self.assertRaises(ValueError):
                self.common.project_path(self.root, path)
        self.assertEqual(self.common.project_path(self.root, 'scenes/current.blend'), self.root / 'scenes/current.blend')

    def test_json_replacement_preserves_unicode_and_is_complete(self):
        path = self.root / 'queue' / 'job.json'
        self.common.write_json(path, {'label': '첫 작업'})
        self.common.write_json(path, {'label': '수정'})
        self.assertEqual(json.loads(path.read_text(encoding='utf-8')), {'label': '수정'})
        self.assertEqual([p.name for p in path.parent.iterdir()], ['job.json'])

    def test_lock_rejects_second_owner_and_releases(self):
        lock = self.root / 'owner.lock'
        with self.common.FileLock(lock):
            with self.assertRaises(BlockingIOError):
                with self.common.FileLock(lock):
                    self.fail('two owners acquired one lock')
        with self.common.FileLock(lock):
            pass

    def test_symlink_escape_is_rejected(self):
        outside = self.root.parent
        try:
            (self.root / 'link').symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest('symlink privilege unavailable')
        with self.assertRaises(ValueError):
            self.common.project_path(self.root, 'link/outside.blend')


if __name__ == '__main__':
    unittest.main()
