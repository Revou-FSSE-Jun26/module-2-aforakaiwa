# Implementation Plan: User Password Hashing

## Overview

Migrate the RevoU Shop registration endpoint from accepting pre-hashed passwords to accepting plain-text passwords with server-side bcrypt hashing. This includes adding password validation (minimum 8 characters), implementing `set_password` and `check_password` methods on the User model, updating the registration route, and ensuring the response never leaks the password hash.

## Tasks

- [x] 1. Add bcrypt dependency and set up test infrastructure
  - [x] 1.1 Add bcrypt to requirements.txt and create test directory
    - Add `bcrypt==4.2.1` to `requirements.txt`
    - Add `hypothesis==6.108.0` and `pytest==8.3.3` to `requirements.txt`
    - Create `tests/` directory with `__init__.py`
    - Create `tests/conftest.py` with Flask test client fixture and in-memory SQLite test database setup
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 2. Implement password hashing methods on User model
  - [x] 2.1 Add `set_password` and `check_password` methods to User model
    - In `models.py`, import `bcrypt`
    - Add `set_password(self, raw_password: str)` method that calls `bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())` and stores the result in `self.password_hash`
    - Add `check_password(self, raw_password: str) -> bool` method that calls `bcrypt.checkpw(raw_password.encode('utf-8'), self.password_hash.encode('utf-8'))` and returns the result
    - Remove any existing Werkzeug password hashing imports if present
    - _Requirements: 2.1, 2.2, 2.3, 4.1, 4.2, 4.3_

  - [ ]* 2.2 Write property test for hash round-trip verification
    - **Property 1: Password hash round-trip verification**
    - Create `tests/test_password_hashing.py`
    - Use Hypothesis strategy `text(min_size=8, max_size=50, alphabet=characters(whitelist_categories=('L', 'N', 'P')))` to generate passwords
    - Assert that `user.check_password(password)` returns True after `user.set_password(password)`
    - **Validates: Requirements 4.1**

  - [ ]* 2.3 Write property test for unique salt per hash
    - **Property 2: Unique salt per hash**
    - In `tests/test_password_hashing.py`, add test that hashes the same password twice and asserts different hash strings
    - Use same Hypothesis strategy as Property 1
    - **Validates: Requirements 2.2, 4.2**

  - [ ]* 2.4 Write property test for valid bcrypt hash format
    - **Property 3: Hash output is valid bcrypt format**
    - In `tests/test_password_hashing.py`, add test that asserts hash starts with `$2b$` and is exactly 60 characters long
    - Use same Hypothesis strategy as Property 1
    - **Validates: Requirements 2.1, 2.3**

- [ ] 3. Implement password validation in registration endpoint
  - [ ] 3.1 Update `create_user` route with password validation and hashing
    - In `routes.py`, modify `create_user()` to accept `password` field instead of `password_hash`
    - Add validation: return 400 if `password` key is missing or empty (falsy)
    - Add validation: return 400 with message "Password must be at least 8 characters long" if `len(password) < 8`
    - On valid password, call `user.set_password(data["password"])` instead of directly assigning `password_hash`
    - Ensure response uses `user.to_dict()` which already excludes `password_hash`
    - Return 201 with success message on successful registration
    - _Requirements: 1.1, 1.2, 1.3, 2.4, 3.1, 3.2, 5.1, 5.2_

  - [ ]* 3.2 Write property test for password length validation boundary
    - **Property 4: Password length validation boundary**
    - In `tests/test_password_hashing.py`, add test using Flask test client
    - Generate short passwords (`text(min_size=1, max_size=7)`) and assert 400 response
    - Generate valid passwords (`text(min_size=8, max_size=50)`) and assert password is accepted for hashing
    - **Validates: Requirements 3.1, 3.2**

  - [ ]* 3.3 Write property test for response excluding password hash
    - **Property 5: Response never contains password hash**
    - In `tests/test_password_hashing.py`, add test using Flask test client
    - Register a user with a valid password and assert `password_hash` key is not in response JSON
    - Use Hypothesis strategy for valid passwords
    - **Validates: Requirements 5.1**

- [ ] 4. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Write unit and integration tests
  - [ ]* 5.1 Write unit tests for registration edge cases
    - Create `tests/test_registration.py`
    - Test missing password field returns 400
    - Test empty password string returns 400
    - Test successful registration returns 201
    - Test successful registration stores bcrypt hash in database (starts with `$2b$`)
    - Test `check_password` method returns False for wrong password
    - Test `check_password` method exists and is callable
    - _Requirements: 1.2, 1.3, 2.4, 4.1, 4.3, 5.2_

- [ ] 6. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The project uses Python with Flask, SQLAlchemy, and PostgreSQL
- bcrypt is the target hashing library (replacing any Werkzeug password utilities)
- The `to_dict()` method on User model already excludes `password_hash` from responses

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["2.2", "2.3", "2.4", "3.1"] },
    { "id": 3, "tasks": ["3.2", "3.3"] },
    { "id": 4, "tasks": ["5.1"] }
  ]
}
```
