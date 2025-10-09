Learning Activities - TODO
=========================

Tasks (short-term, prioritized):

- [x] Add unit tests for LearningActivityService (covers create, submit, grade, progress)
- [x] Add a simple test runner for environments without pytest
- [ ] Convert and add pytest-friendly tests that can run in CI using monkeypatch (done below)
- [ ] Wire additional endpoints to the service layer (grading endpoints, activity listing by course)
- [ ] Add type hints to `services.py` and improve docstrings
- [ ] Add integration tests for routes (use Flask test client)

Notes:
- The tests inject fake model classes into sys.modules to avoid relying on mongoengine/MongoDB during unit tests.
