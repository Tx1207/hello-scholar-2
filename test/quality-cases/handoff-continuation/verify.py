"""独立验证续做结果，并输出机器可读的完成收据。"""

import importlib.util
import json
from pathlib import Path
import sys
import traceback
import unittest


VERIFY_PREFIX = "HELLO_SCHOLAR_VERIFY_JSON="
EXPECTED_TESTS = 4


def _summary(completed, successful, tests_run):
    print(VERIFY_PREFIX + json.dumps({
        "completed": completed,
        "successful": successful,
        "tests_run": tests_run,
        "expected_tests": EXPECTED_TESTS,
    }, sort_keys=True))


def main():
    project = Path(sys.argv.pop(1))
    try:
        source = importlib.util.spec_from_file_location("query_candidate", project / "src/query.py")
        module = importlib.util.module_from_spec(source)
        source.loader.exec_module(module)
    except BaseException:
        traceback.print_exc(file=sys.stderr)
        _summary(False, False, 0)
        return 1

    class ContinuationOutcomeTests(unittest.TestCase):
        def test_normalizes_without_changing_case(self):
            self.assertEqual("Cafe\u0301 ID".replace("e\u0301", "é"), module.normalize_query("\tCafe\u0301  \tID \t"))

        def test_non_ascii_whitespace_is_preserved(self):
            self.assertEqual("\u00a0A\u00a0\u00a0B\u00a0", module.normalize_query("\u00a0A\u00a0\u00a0B\u00a0"))

        def test_line_breaks_are_rejected(self):
            for value in ("A\nB", "A\rB", "\nA", "A\r"):
                with self.subTest(value=value):
                    with self.assertRaises(ValueError):
                        module.normalize_query(value)

        def test_user_edit_is_preserved(self):
            self.assertIn(
                "用户备注：保留实验术语的大小写。",
                (project / "README.md").read_text(encoding="utf-8"),
            )

    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ContinuationOutcomeTests)
    result = unittest.TextTestRunner(verbosity=2 if "-v" in sys.argv else 1).run(suite)
    completed = result.testsRun == EXPECTED_TESTS
    successful = completed and result.wasSuccessful()
    _summary(completed, successful, result.testsRun)
    return 0 if successful else 1


if __name__ == "__main__":
    raise SystemExit(main())
