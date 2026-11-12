import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "handoff_package.py"
SPEC = importlib.util.spec_from_file_location("handoff_package", MODULE_PATH)
handoff_package = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(handoff_package)


class HandoffPackageTests(unittest.TestCase):
    def make_package(self, root: Path):
        for name in ("device.dra", "device.psm", "signal.pad"):
            (root / name).write_bytes((name + "\n").encode())

    def test_snapshot_and_verify(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_package(root)
            manifest = handoff_package.snapshot(root, ["device.dra", "device.psm", "signal.pad"])
            self.assertEqual(handoff_package.verify(root, manifest), [])

    def test_detects_changed_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.make_package(root)
            manifest = handoff_package.snapshot(root, ["device.dra", "device.psm", "signal.pad"])
            (root / "signal.pad").write_text("changed", encoding="utf-8")
            self.assertEqual(handoff_package.verify(root, manifest), ["CHANGED: signal.pad"])

    def test_requires_native_roles(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "device.dra").write_text("source", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required roles"):
                handoff_package.snapshot(root, ["device.dra"])


if __name__ == "__main__":
    unittest.main()

