# Requirements Document

## Introduction

This document specifies the requirements for the user login feature of the RevoU Shop application. The feature provides a POST /auth/login endpoint that authenticates users by verifying their email and password against the stored bcrypt hash, and returns a JWT token upon successful authentication.

## Glossary

- **Login_Endpoint**: The HTTP POST endpoint at /auth/login that accepts user credentials and returns authentication tokens
- **Auth_Service**: The authentication service module responsible for credential verification and token generation
- **JWT_Token**: A JSON Web Token issued to authenticated users, containing user identity claims and an expiration timestamp
- **Request_Body**: The JSON payload sent to the Login_Endpoint containing user credentials
- **User_Record**: A row in the users table containing user_id, username, full_name, role, email, password_hash, is_active, and created_at

## Requirements

### Requirement 1: Accept Login Credentials

**User Story:** As a registered user, I want to submit my email and password to the login endpoint, so that I can authenticate and access protected resources.

#### Acceptance Criteria

1. WHEN a POST request is sent to /auth/login with a JSON Request_Body containing "email" and "password" fields, THE Login_Endpoint SHALL accept the request for processing
2. IF the Request_Body is missing the "email" field, THEN THE Login_Endpoint SHALL return HTTP 400 with an error message indicating the email field is required
3. IF the Request_Body is missing the "password" field, THEN THE Login_Endpoint SHALL return HTTP 400 with an error message indicating the password field is required
4. IF the Request_Body is not valid JSON or is empty, THEN THE Login_Endpoint SHALL return HTTP 400 with an error message indicating invalid request format

### Requirement 2: Verify User Credentials

**User Story:** As a registered user, I want the system to verify my password against the stored hash, so that only I can access my account.

#### Acceptance Criteria

1. WHEN valid credentials are submitted, THE Auth_Service SHALL query the User_Record by the provided email address
2. WHEN a User_Record matching the email is found, THE Auth_Service SHALL verify the provided password against the stored password_hash using bcrypt comparison
3. IF no User_Record with the provided email exists, THEN THE Login_Endpoint SHALL return HTTP 401 with an error message "Invalid email or password"
4. IF the provided password does not match the stored password_hash, THEN THE Login_Endpoint SHALL return HTTP 401 with an error message "Invalid email or password"

### Requirement 3: Enforce Active Account Requirement

**User Story:** As a system administrator, I want inactive accounts to be blocked from logging in, so that deactivated users cannot access the system.

#### Acceptance Criteria

1. WHEN credentials are verified successfully, THE Auth_Service SHALL check the is_active field of the User_Record
2. IF the User_Record has is_active set to false, THEN THE Login_Endpoint SHALL return HTTP 403 with an error message "Account is inactive"

### Requirement 4: Generate JWT Token on Successful Authentication

**User Story:** As an authenticated user, I want to receive a JWT token after login, so that I can use it to access protected endpoints without re-authenticating.

#### Acceptance Criteria

1. WHEN credentials are verified and the account is active, THE Auth_Service SHALL generate a JWT_Token containing the user_id, email, and role claims
2. THE Auth_Service SHALL sign the JWT_Token using a secret key stored in the application configuration
3. THE Auth_Service SHALL set the JWT_Token expiration to a configurable duration (default 24 hours from the time of issuance)

### Requirement 5: Return Successful Login Response

**User Story:** As an authenticated user, I want to receive my profile information along with the token, so that the client application can display my details without an additional request.

#### Acceptance Criteria

1. WHEN authentication is successful, THE Login_Endpoint SHALL return HTTP 200 with a JSON response body
2. THE Login_Endpoint SHALL include the JWT_Token in the response body under the "token" key
3. THE Login_Endpoint SHALL include a "user" object in the response body containing: user_id, username, full_name, email, and role
4. THE Login_Endpoint SHALL exclude the password_hash from the response body

### Requirement 6: Handle Unexpected Errors

**User Story:** As a developer, I want the login endpoint to handle unexpected errors gracefully, so that internal details are not exposed to clients.

#### Acceptance Criteria

1. IF an unexpected error occurs during authentication processing, THEN THE Login_Endpoint SHALL return HTTP 500 with a generic error message "An internal error occurred"
2. IF an unexpected error occurs, THEN THE Login_Endpoint SHALL log the error details for debugging purposes without exposing the details in the response
