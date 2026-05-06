import os
import sqlite3

from dotenv import load_dotenv
load_dotenv()

_DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "enquiry.db")
DB_PATH = os.getenv("DB_PATH", _DEFAULT_DB)


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def log_lead(client_id, source, name, phone, email,
             business_type, pain_point, message, budget, timeframe):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO leads
                (client_id, source, name, phone, email,
                 business_type, pain_point, message, budget, timeframe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (client_id, source, name, phone, email,
             business_type, pain_point, message, budget, timeframe),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def log_qualification(lead_id, score, decision, reason):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO qualifications (lead_id, score, decision, reason)
            VALUES (?, ?, ?, ?)
            """,
            (lead_id, score, decision, reason),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def log_conversation(lead_id, client_id, direction, channel,
                     sender, message_content, status="sent"):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO conversations
                (lead_id, client_id, direction, channel, sender, message_content, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (lead_id, client_id, direction, channel, sender, message_content, status),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def log_response(lead_id, client_id, channel, recipient_type,
                 recipient_contact, message_content, generated_by, status="sent"):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO responses
                (lead_id, client_id, channel, recipient_type,
                 recipient_contact, message_content, generated_by, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (lead_id, client_id, channel, recipient_type,
             recipient_contact, message_content, generated_by, status),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update_lead_status(lead_id, status):
    conn = _connect()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE leads SET status = ? WHERE id = ?",
            (status, lead_id),
        )
        conn.commit()
    finally:
        conn.close()
