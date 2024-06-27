import json
import sqlite3
from datetime import datetime, timedelta, timezone
from gmail_api import main


def create_connection(db_file):
    """Create a database connection to a SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Create a table for storing emails."""
    create_emails_table_sql = """
    CREATE TABLE IF NOT EXISTS emails (
        msg_id TEXT PRIMARY KEY,
        sender TEXT NOT NULL,
        subject TEXT NOT NULL,
        snippet TEXT,
        date_received TEXT NOT NULL
    );
    """
    try:
        c = conn.cursor()
        c.execute(create_emails_table_sql)
    except sqlite3.Error as e:
        print(e)

def insert_email(conn, email):
    """Insert an email into the emails table."""
    sql = ''' INSERT OR REPLACE INTO emails(msg_id, sender, subject, snippet, date_received)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (email['msg_id'], email['sender'], email['subject'], email['snippet'], email['date_received']))
    conn.commit()

def fetch_emails_from_db(conn):
    """Fetch all emails from the emails table."""
    cur = conn.cursor()
    cur.execute("SELECT msg_id, sender, subject, snippet, date_received FROM emails")
    rows = cur.fetchall()
    emails = []
    for row in rows:
        emails.append({
            'msg_id': row[0],
            'sender': row[1],
            'subject': row[2],
            'snippet': row[3],
            'date_received': row[4]
        })
    return emails


def parse_email_datetime(email_datetime_str):
    """Parse email datetime string into a datetime object."""
    try:
        return datetime.strptime(email_datetime_str, '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        return datetime.strptime(email_datetime_str, '%a, %d %b %Y %H:%M:%S')

def match_condition(email, condition):
    """Check if an email matches a single condition."""
    field = condition['field']
    predicate = condition['predicate']
    value = condition['value']
    email_value = email[field]

    if field == 'date_received':
        email_date = parse_email_datetime(email_value)
        
        if predicate == 'less than':
            current_datetime_utc = datetime.now(timezone.utc)
            return email_date < current_datetime_utc - timedelta(days=int(value))
        elif predicate == 'greater than':
            current_datetime_utc = datetime.now(timezone.utc)
            return email_date > current_datetime_utc - timedelta(days=int(value))
    else:
        if predicate == 'contains':
            return value.lower() in email_value.lower()
        elif predicate == 'does not contain':
            return value.lower() not in email_value.lower()
        elif predicate == 'equals':
            return email_value.lower() == value.lower()
        elif predicate == 'does not equal':
            return email_value.lower() != value.lower()

    return False

def print_email_info(email, message):
    """Print formatted email information."""
    formatted_message = message.format(email_id=email['msg_id'], date_received=email['date_received'])
    print(formatted_message)

def process_emails():
    """Process emails based on rules defined in a JSON file."""
    with open('rules.json') as f:
        rules = json.load(f)

    database = "emails.db"
    conn = create_connection(database)
    if conn is not None:
        emails = fetch_emails_from_db(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")
        return

    for email in emails:
        for rule in rules:
            rule_predicate = rule['predicate']
            conditions = rule.get('conditions', [])
            actions = rule.get('actions', [])

            if (rule_predicate == 'All' and all(match_condition(email, condition) for condition in conditions)) or \
               (rule_predicate == 'Any' and any(match_condition(email, condition) for condition in conditions)):
                
                for action in actions:
                    if action['action'] == 'print_email_info':
                        print_email_info(email, action['message'])

if __name__ == '__main__':
    emails = main()
    
    database = "emails.db"
    conn = create_connection(database)
    if conn is not None:
        create_table(conn)
        for email in emails:
            insert_email(conn, email)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")
    process_emails()
