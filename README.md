# Gmail Email Processor

## Overview

This Python script integrates with the Gmail API to fetch emails, store them in an SQLite database, and process them based on rules defined in a JSON file.

## Prerequisites

1. Python 3 installed on your machine.
2. Gmail API credentials.

## Installation

1. Clone the repository or download the script files.
2. Install the required libraries using pip:
   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
3. Obtain OAuth 2.0 client credentials from the Google Cloud Console and save the JSON file as `credentials.json` in the same directory as the script.

## Usage

1. Run the script to authenticate with Gmail and fetch emails:
   python main.py

2. Define your rules in a `rules.json` file. Here is an example:
   [
    {
        "predicate": "All",
        "conditions": [
            {"field": "sender", "predicate": "contains", "value": "example.com"},
            {"field": "subject", "predicate": "does not contain", "value": "spam"}
        ],
        "actions": [
            {"type": "mark_as_read"}
        ]
    },
    {
        "predicate": "Any",
        "conditions": [
            {"field": "message", "predicate": "contains", "value": "urgent"},
            {"field": "date_received", "predicate": "less than", "value": "7"}
        ],
        "actions": [
            {"type": "mark_as_unread"},
            {"type": "move_message", "label_id": "Label_1"}
        ]
    }
]

3. Run the processing.py script to fetch and process the emails based on the defined rules:
  python processing.py


## Notes

- Using `eval` and `exec` can be dangerous if not handled properly. This script assumes a controlled environment where the rules are safe to execute. In a real-world scenario, ensure to validate and sanitize the input properly.
- This script lacks detailed error handling for simplicity. In a production scenario, add comprehensive error handling and logging.
- The example uses SQLite for storing emails. Adjust the database connection and storage logic as per your needs and preferences.


