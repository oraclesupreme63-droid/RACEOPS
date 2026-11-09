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
round-trips. HTTP integration tests exercise login, multiple-team selection,
current identity, indistinguishable credential failures, token rejection and
immediate Role changes against PostgreSQL. Authorization tests cover all five
Roles, deny-by-default permissions, Team isolation, relationship checks and
the three Visibility levels. Configuration and HTTP tests also verify that
production rejects development or weak secrets and that CORS allows only
configured origins while exposing the request correlation header.

Operational persistence coverage validates Driver, Vehicle, Track and Event
defaults, timestamps, Team-scoped uniqueness, same-Team Driver/User and
Event/Track relations, valid Event dates, restrictive historical references
and the Alembic migration round-trip.

Driver HTTP coverage exercises create, list, read, update, activate and
deactivate; stable pagination; status filtering; same-Team User links; all
five Roles; Driver self-scope; cross-Team hiding; safe link conflicts; request
validation and the deliberate absence of DELETE. Logging tests also verify
that Alembic cannot leave the RaceOps logger namespace disabled.

Vehicle HTTP coverage exercises create, list, read, rename and every explicit
availability command; the complete transition matrix; terminal retirement;
same-Team identifier uniqueness; Administrator and Team Manager management;
Engineer and Mechanic read-only access; Driver denial until a Session
relationship exists; cross-Team hiding; request validation and the deliberate
absence of DELETE. Unit tests keep `READY` as the only assignable state.

Track and Event HTTP coverage exercises catalog creation and updates, optional
location, same-Team Track links, date validation, filtering, the complete
Event transition matrix, terminal states, all five Roles, Driver relationship
deferral, cross-Team hiding, request validation and the absence of DELETE.

Database integration tests are opt-in so the ordinary unit suite remains
usable without Docker. With the PostgreSQL service healthy, run:

```powershell
$env:RACEOPS_RUN_DB_TESTS = "1"
.\.venv\Scripts\python.exe -m pytest
Remove-Item Env:RACEOPS_RUN_DB_TESTS
```

