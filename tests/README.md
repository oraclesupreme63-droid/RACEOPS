# RaceOps tests

Tests will be organized by responsibility rather than by implementation
file:

- `unit/`: pure domain rules and value objects;
- `integration/`: PostgreSQL, mappings, transactions and migrations;
- `api/`: HTTP contracts, authentication and error responses;
- `acceptance/`: complete user-visible flows;
- `factories/`: deterministic synthetic test data.

Directories will be created when their first real test is added. Empty test
packages are intentionally avoided.

Database integration tests are opt-in so the ordinary unit suite remains
usable without Docker. With the PostgreSQL service healthy, run:

```powershell
$env:RACEOPS_RUN_DB_TESTS = "1"
.\.venv\Scripts\python.exe -m pytest
Remove-Item Env:RACEOPS_RUN_DB_TESTS
```

