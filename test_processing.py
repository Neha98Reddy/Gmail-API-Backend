import unittest
import sqlite3
import json
from datetime import datetime, timezone, timedelta
from processing import create_connection, create_table, insert_email, fetch_emails_from_db, parse_email_datetime, match_condition, process_emails

class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        """Set up a temporary database for testing."""
        self.database = ":memory:"
        self.conn = create_connection(self.database)
        create_table(self.conn)
    
    def tearDown(self):
        """Close the database connection."""
        self.conn.close()

    def test_create_connection(self):
        """Test creating a database connection."""
        conn = create_connection(self.database)
        self.assertIsNotNone(conn)
        conn.close()

    def test_create_table(self):
        """Test creating the emails table."""
        create_table(self.conn)
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='emails';")
        table = cur.fetchone()
        self.assertIsNotNone(table)

    def test_insert_email(self):
        """Test inserting an email into the database."""
        email = {
            'msg_id': '123',
            'sender': 'nehareddy123@gmail.com',
            'subject': 'Test Email',
            'snippet': 'This is a test email.',
            'date_received': 'Thu, 27 Jun 2024 10:09:27 +0530'
        }
        insert_email(self.conn, email)
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM emails WHERE msg_id=?", (email['msg_id'],))
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row[1], email['sender'])

    def test_fetch_emails_from_db(self):
        """Test fetching emails from the database."""
        email = {
            'msg_id': '123',
            'sender': 'nehaeereddy@gmail.com',
            'subject': 'Test Email',
            'snippet': 'This is a test email.',
            'date_received': 'Thu, 27 Jun 2024 10:09:27 +0340'
        }
        insert_email(self.conn, email)
        emails = fetch_emails_from_db(self.conn)
        self.assertEqual(len(emails), 1)
        self.assertEqual(emails[0]['msg_id'], email['msg_id'])

class TestEmailProcessing(unittest.TestCase):

    def test_parse_email_datetime(self):
        """Test parsing email datetime."""
        datetime_str = 'Thu, 27 Jun 2024 10:09:27 +0240'
        expected_datetime = datetime(2024, 6, 27, 10, 9, 27, tzinfo=timezone.utc)
        parsed_datetime = parse_email_datetime(datetime_str)
        self.assertEqual(parsed_datetime, expected_datetime)

    def test_match_condition(self):
        """Test matching conditions."""
        email = {
            'msg_id': '123',
            'sender': 'test@example.com',
            'subject': 'Test Email',
            'snippet': 'This is a test email.',
            'date_received': 'Thu, 27 Jun 2024 10:09:27 +0210'
        }
        condition = {
            'field': 'subject',
            'predicate': 'contains',
            'value': 'Test'
        }
        self.assertTrue(match_condition(email, condition))

        condition = {
            'field': 'subject',
            'predicate': 'does not contain',
            'value': 'NotInSubject'
        }
        self.assertTrue(match_condition(email, condition))

        condition = {
            'field': 'date_received',
            'predicate': 'less than',
            'value': '1'
        }
        self.assertTrue(match_condition(email, condition))

    def test_process_emails(self):
        """Test processing emails based on rules."""
        # Create a temporary database and insert a test email
        database = ":memory:"
        conn = create_connection(database)
        create_table(conn)
        email = {
            'msg_id': '123',
            'sender': 'nehareddy@gmail.com',
            'subject': 'Test Email',
            'snippet': 'This is a test email.',
            'date_received': 'Thu, 27 Jun 2024 10:09:27 +0111'
        }
        insert_email(conn, email)
        conn.close()

        # Create a mock rules.json file
        rules = [
            {
                'predicate': 'All',
                'conditions': [
                    {
                        'field': 'subject',
                        'predicate': 'contains',
                        'value': 'Test'
                    }
                ],
                'actions': [
                    {
                        'action': 'print_email_info',
                        'message': 'Email ID: {email_id}, Date Received: {date_received}'
                    }
                ]
            }
        ]
        with open('rules.json', 'w') as f:
            json.dump(rules, f)

        # Capture the printed output
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output

        # Process emails
        process_emails()

        # Check if the output is as expected
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue().strip()
        expected_output = 'Email ID: 123, Date Received: Thu, 27 Jun 2024'
        self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main()
