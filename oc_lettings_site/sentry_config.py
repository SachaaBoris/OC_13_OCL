import os
from datetime import datetime
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration


def add_timestamp(event, hint):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add timestamp to tags
    if 'tags' not in event:
        event['tags'] = {}
    event['tags']['timestamp'] = timestamp

    # Add timestamp to added data
    if 'extra' not in event:
        event['extra'] = {}
    event['extra']['timestamp'] = timestamp

    # Add timestamp to message
    if event.get('message'):
        event['message'] = f"{event['message']} [Horodatage: {timestamp}]"

    return event


def initialize_sentry(env_str):
    """Initialize Sentry with timestamp configuration"""
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        environment=env_str,
        send_default_pii=True,
        before_send=add_timestamp
    )
