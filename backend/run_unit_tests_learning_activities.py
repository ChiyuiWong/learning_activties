"""Simple test runner for learning_activities service tests without pytest.

This runner imports the test module and calls test functions manually so tests
can run even when pytest is not available in the execution environment.
"""
import importlib
import importlib.util
import os
import traceback

def run():
    # Load the test module by file path to avoid importing the package root
    test_path = os.path.join(os.path.dirname(__file__), 'app', 'modules', 'learning_activities', 'test_services.py')
    spec = importlib.util.spec_from_file_location('test_services', test_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    failures = []
    successes = []

    for name in dir(mod):
        if name.startswith('test_'):
            func = getattr(mod, name)
            if callable(func):
                try:
                    # Provide a simple monkeypatch object for tests that expect it
                    class MonkeyPatch:
                        def setattr(self, target, name, value):
                            # Accept either (module_obj, attr_name, value) or
                            # (dotted.module.path, attr_name, value)
                            if isinstance(target, str):
                                parts = target.split('.')
                                module = __import__('.'.join(parts[:-1]), fromlist=[parts[-1]]) if len(parts) > 1 else globals()
                                setattr(module, name, value)
                            else:
                                setattr(target, name, value)

                    import inspect
                    params = inspect.signature(func).parameters
                    if len(params) == 1:
                        func(MonkeyPatch())
                    else:
                        func()
                    successes.append(name)
                except Exception:
                    failures.append((name, traceback.format_exc()))

    print('Ran', len(successes) + len(failures), 'tests:', len(successes), 'passed,', len(failures), 'failed')
    if failures:
        for name, tb in failures:
            print('\nFAILED:', name)
            print(tb)
        raise SystemExit(1)

if __name__ == '__main__':
    run()
