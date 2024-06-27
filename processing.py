import json
from datetime import datetime, timedelta, timezone
from gmail_api import main

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

def process_emails(emails):
    """Process emails based on rules defined in a JSON file."""
    with open('rules.json') as f:
        rules = json.load(f)

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
    emails=main()
    process_emails(emails)
