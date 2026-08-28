# Requirements Document

## Introduction

This feature implements server-side password hashing for user registration in the RevoU Shop application. Currently, the registration endpoint accepts a pre-hashed password from the client. This feature changes the API to accept a plain-text password from the client and hash it server-side using bcrypt before storing it in the database. The stored hash can later be used for password verification during login.

## Glossary

- **Registration_Endpoint**: The POST /users API route that creates a new user account
- **Password_Hasher**: The server-side component responsible for hashing plain-text passwords using bcrypt
- **Password_Hash**: The bcrypt-encoded string stored in the database representing the user's password
- **Plain_Text_Password**: The raw password string submitted by the client in the registration request body

## Requirements

### Requirement 1: Accept Plain-Text Password During Registration

**User Story:** As a new user, I want to submit my password in plain text during registration, so that the server securely hashes it for me.

#### Acceptance Criteria

1. WHEN a registration request is received with a "password" field, THE Registration_Endpoint SHALL accept the plain-text password from the request body
2. WHEN a registration request is received without a "password" field, THE Registration_Endpoint SHALL return a 400 status code with an error message indicating the missing field
3. WHEN a registration request is received with an empty "password" field, THE Registration_Endpoint SHALL return a 400 status code with an error message indicating the password is invalid

### Requirement 2: Hash Password Server-Side Before Storage

**User Story:** As a system administrator, I want passwords to be hashed on the server before storage, so that plain-text passwords are never persisted in the database.

#### Acceptance Criteria

1. WHEN a valid registration request is received, THE Password_Hasher SHALL hash the plain-text password using bcrypt before storing it in the database
2. THE Password_Hasher SHALL generate a unique salt for each password hash
3. THE Password_Hash stored in the database SHALL be a valid bcrypt hash string (starting with "$2b$")
4. THE Registration_Endpoint SHALL store the hashed password in the password_hash column of the users table

### Requirement 3: Password Validation Rules

**User Story:** As a system administrator, I want minimum password requirements enforced, so that users create sufficiently strong passwords.

#### Acceptance Criteria

1. WHEN a registration request contains a password shorter than 8 characters, THE Registration_Endpoint SHALL return a 400 status code with an error message indicating the password is too short
2. WHEN a registration request contains a password of 8 characters or more, THE Registration_Endpoint SHALL accept the password for hashing

### Requirement 4: Password Hash Verification Support

**User Story:** As a developer, I want the stored hash to be verifiable against the original password, so that future login functionality can authenticate users.

#### Acceptance Criteria

1. FOR ALL valid plain-text passwords, hashing then verifying the plain-text password against the stored hash SHALL return a positive match (round-trip property)
2. FOR ALL valid plain-text passwords, hashing the same password twice SHALL produce different hash strings due to unique salts
3. THE Password_Hasher SHALL provide a verification function that compares a plain-text password against a stored hash

### Requirement 5: Registration Response Excludes Password

**User Story:** As a developer, I want the API response to never include the password or hash, so that sensitive data is not leaked through the API.

#### Acceptance Criteria

1. WHEN a user is successfully registered, THE Registration_Endpoint SHALL return the user data without the password_hash field in the response
2. WHEN a user is successfully registered, THE Registration_Endpoint SHALL return a 201 status code with a success message
