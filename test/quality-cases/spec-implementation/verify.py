"""Run the handoff fixture's private verifier without copying its contract."""

import importlib.util
from pathlib import Path


def main():
    verifier = Path(__file__).parents[1] / "handoff-continuation/verify.py"
    spec = importlib.util.spec_from_file_location("handoff_private_verify", verifier)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main()


if __name__ == "__main__":
    raise SystemExit(main())
