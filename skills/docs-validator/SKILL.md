---
name: docs-validator
description: Validates that all new technologies, architectural changes, and major code additions are documented in the `docs/` learning center. Use before finalizing a PR.
---

# Documentation Validator Assistant

This skill ensures that the "Tech Learning Center" (`docs/` folder) remains up to date with the evolving implementation of the project.

## Workflow

1. **Scan for Changes**:
   - Compare the current feature branch against the base branch (`master`).
   - Identify new libraries, third-party packages, or architectural patterns introduced.

2. **Check Documentation Coverage**:
   - Verify if the new technologies are documented in the appropriate subfolder within `docs/`.
   - Ensure that the `docs/index.md` (Hub) is updated to link to the new documentation.

3. **Verify Content Quality**:
   - Documentation must explain the **What**, **Why**, and **How** of the technology.
   - Check for consistent formatting and navigation links.

4. **Report Findings**:
   - Provide a list of missing documentation items.
   - Propose specific file paths and titles for new documentation if needed.

## Guidelines for Validation

- **New Application/Library**: Must have an entry in `docs/` (or be nested under a relevant category).
- **New Third-Party Package**: Should be added to `docs/python/packages/overview.md` or have its own page if it's significant.
- **Infrastructure Change**: (e.g., new Docker container, new CI/CD step) Must be documented in `docs/infrastructure/`.
- **Database Schema Change**: Must update `docs/database/timescaledb.md` or related files.

## Example Report
"Validation complete. The following items require documentation:
- Missing: Guide for 'Redis' introduced in `apps/api`.
- Action: Create `docs/infrastructure/redis.md` and link it in `docs/index.md`."

---
*Created on: April 8, 2026*
