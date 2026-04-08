# API & Authentication

## What is an API?
An **API (Application Programming Interface)** is a set of rules that allow one piece of software to talk to another. In our case, our code talks to the **EODHD** servers to request financial data.

## HTTP Status Codes
When we make a request to an API, the server responds with a 3-digit **Status Code**. These codes tell us if the request was successful, or if something went wrong.

### The Categories:
- **2xx (Success)**: Everything worked!
    - `200 OK`: Standard success response.
- **3xx (Redirection)**: The resource has moved.
- **4xx (Client Error)**: You made a mistake in the request.
    - `400 Bad Request`: The server didn't understand the parameters.
    - `401 Unauthorized`: Your API key is missing or invalid.
    - `404 Not Found`: The endpoint or ticker symbol doesn't exist.
    - `429 Too Many Requests`: You hit your rate limit.
- **5xx (Server Error)**: The API provider's server is having trouble.
    - `500 Internal Server Error`: A generic error on the provider's side.
    - `503 Service Unavailable`: The server is temporarily down for maintenance.

### Handling in this Project
Our `EODHDClientBase` automatically checks these codes. If it sees a `429`, it knows to wait; if it sees a `401`, it raises a specific `EODHDUnauthorizedError` to alert you that your key is wrong.

## What is an API Key?
Think of an **API Key** like a long, complex password that identifies our application to the data provider. It allows the provider to track our usage and ensure we are authorized to access the data.

### ⚠️ Security Warning
**API Keys are sensitive secrets.** If someone steals your key, they can use your account's credits or access restricted data.
- **NEVER** commit an API key to git.
- **NEVER** share an API key in plain text (e.g., Slack, Email).
- **ALWAYS** use environment variables or `.env` files.

## Local Configuration
We use a `.env` file to store our keys locally. This file is ignored by git (via `.gitignore`) to prevent accidental leaks.

Example `.env` structure:
```env
EODHD_API_KEY=your_secret_key_here
```

## Implementation in this Project
Our `EODHDClientBase` automatically reads this key and attaches it to every request. To protect your privacy during development, our logger is configured to **redact** the API key, so it never appears in your terminal output or log files:

```text
# Example Log Output:
Making request to URL: https://eodhd.com/api/... with params: {'api_token': '### REDACTED ###'}
```
