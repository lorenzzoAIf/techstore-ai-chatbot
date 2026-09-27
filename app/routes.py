from flask import Blueprint, jsonify, render_template, request

from .services.ai_service import AIService
from .services.calendar_service import CalendarService
from .services.contact_service import init_database, save_contact


main = Blueprint("main", __name__)


@main.route("/")
def index():
    """
    Serves the main chatbot interface.
    """
    return render_template("index.html")


@main.route("/api/chat", methods=["POST"])
def chat():
    """
    Receives a customer message and returns an AI response.
    """

    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()

    session_id = data.get("session_id", "default")

    if not message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    if len(message) > 2000:
        return jsonify({
            "error": "Message is too long."
        }), 400

    try:
        ai_service = AIService()

        reply = ai_service.generate_response(
            message,
            session_id=session_id
        )

        return jsonify({
            "reply": reply
        })

    except Exception as error:
        print(f"AI error: {error}")

        return jsonify({
            "error": "The assistant is temporarily unavailable."
        }), 500


@main.route("/api/appointments", methods=["POST"])
def create_appointment():
    """
    Saves customer information and creates
    a Google Calendar appointment.
    """

    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()
    date = data.get("date", "").strip()
    time = data.get("time", "").strip()
    message = data.get("message", "").strip()

    if not name:
        return jsonify({
            "error": "Name is required."
        }), 400

    if not email:
        return jsonify({
            "error": "Email is required."
        }), 400

    if not date:
        return jsonify({
            "error": "Appointment date is required."
        }), 400

    if not time:
        return jsonify({
            "error": "Appointment time is required."
        }), 400

    try:
        init_database()

        contact_id = save_contact(
            name=name,
            email=email,
            phone=phone,
            message=message,
        )

        calendar_service = CalendarService()

        appointment = calendar_service.create_appointment(
            name=name,
            email=email,
            phone=phone,
            date=date,
            time=time,
            message=message,
        )

        return jsonify({
            "message": "Appointment successfully booked.",
            "contact_id": contact_id,
            "calendar_event_id": appointment["id"],
        })

    except Exception as error:
        print(f"Appointment error: {error}")

        return jsonify({
            "error": "The appointment could not be created."
        }), 500