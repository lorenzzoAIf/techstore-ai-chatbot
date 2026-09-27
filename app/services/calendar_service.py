import os
from datetime import datetime, timedelta

from flask import current_app
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/calendar"
]


class CalendarService:
    """
    Handles Google Calendar operations.
    """

    def __init__(self):
        self.credentials_file = current_app.config[
            "GOOGLE_CREDENTIALS_FILE"
        ]

        self.token_file = current_app.config[
            "GOOGLE_TOKEN_FILE"
        ]

        self.calendar_id = current_app.config[
            "GOOGLE_CALENDAR_ID"
        ]

    def _get_credentials(self):
        """
        Loads existing Google credentials or starts
        the OAuth authorization flow.
        """

        credentials = None

        if os.path.exists(self.token_file):
            credentials = Credentials.from_authorized_user_file(
                self.token_file,
                SCOPES
            )

        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())

        if not credentials or not credentials.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file,
                SCOPES
            )

            credentials = flow.run_local_server(
                port=0
            )

            with open(self.token_file, "w") as token:
                token.write(credentials.to_json())

        return credentials

    def _get_service(self):
        """
        Creates the Google Calendar API service.
        """

        credentials = self._get_credentials()

        return build(
            "calendar",
            "v3",
            credentials=credentials
        )

    def create_appointment(
        self,
        name: str,
        email: str,
        phone: str,
        date: str,
        time: str,
        message: str = ""
    ):
        """
        Creates an appointment in Google Calendar.
        """

        service = self._get_service()

        start_datetime = datetime.fromisoformat(
            f"{date}T{time}"
        )

        end_datetime = start_datetime + timedelta(
            minutes=30
        )

        event = {
            "summary": f"Appointment with {name}",

            "description": (
                f"Customer: {name}\n"
                f"Email: {email}\n"
                f"Phone: {phone}\n\n"
                f"Message:\n{message}"
            ),

            "start": {
                "dateTime": start_datetime.isoformat(),
                "timeZone": "Europe/Paris",
            },

            "end": {
                "dateTime": end_datetime.isoformat(),
                "timeZone": "Europe/Paris",
            },

            "attendees": [
                {
                    "email": email,
                    "displayName": name,
                }
            ],
        }

        created_event = service.events().insert(
            calendarId=self.calendar_id,
            body=event,
            sendUpdates="all",
        ).execute()

        return {
            "id": created_event.get("id"),
            "html_link": created_event.get("htmlLink"),
        }
