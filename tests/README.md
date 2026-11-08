# RaceOps tests

Tests are organized by responsibility rather than by implementation file:

- `unit/`: pure domain rules and value objects;
- `integration/`: PostgreSQL, mappings, transactions and migrations;
- `api/`: HTTP contracts, authentication and error responses;
- `acceptance/`: complete user-visible flows;
- `factories/`: deterministic synthetic test data.

Identity coverage includes persistence, Argon2id credentials, JWT claim and
signature validation, current server-side identity resolution, role changes,
inactive boundaries, atomic administrative bootstrap and migration
round-trips.

Database integration tests are opt-in so the ordinary unit suite remains
usable without Docker. With the PostgreSQL service healthy, run:

```powershell
$env:RACEOPS_RUN_DB_TESTS = "1"
.\.venv\Scripts\python.exe -m pytest
Remove-Item Env:RACEOPS_RUN_DB_TESTS
```

