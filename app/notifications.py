from flask import current_app
from flask_mail import Message


def notify_admin(subject, body):
    try:
        from app import mail
        msg = Message(
            subject=f'[Edcar Properties] {subject}',
            recipients=[current_app.config['ADMIN_EMAIL']],
            body=body
        )
        mail.send(msg)
    except Exception as e:
        print(f'Email error: {e}')


def notify_new_agent(user):
    notify_admin(
        'New Agent Registered',
        f'New agent registered:\n\nName: {user.name}\nEmail: {user.email}\nPhone: {user.phone}'
    )


def notify_payment_uploaded(user, amount):
    notify_admin(
        'Payment Proof Uploaded',
        f'Payment proof uploaded:\n\nName: {user.name}\nEmail: {user.email}\nPhone: {user.phone}\nAmount: ${amount}'
    )


def notify_property_submitted(user, prop):
    notify_admin(
        'New Property Submitted',
        f'New property submitted:\n\nAgent: {user.name}\nTitle: {prop.title}\nType: {prop.listing_type}\nLocation: {prop.location}\nPrice: {prop.price}'
    )


def notify_new_inquiry(inquiry, reference):
    notify_admin(
        f'New Inquiry — {reference}',
        f'New inquiry received:\n\nFrom: {inquiry.visitor_name}\nEmail: {inquiry.visitor_email}\nPhone: {inquiry.visitor_phone}\nRe: {reference}\n\nMessage:\n{inquiry.message}'
    )


def notify_user_activated(user):
    try:
        from app import mail
        msg = Message(
            subject='Your Edcar Properties Account is Active!',
            recipients=[user.email],
            body=f'Hi {user.name},\n\nYour account has been activated. You can now submit property listings on Edcar Properties.\n\nVisit: https://edcarproperties.co.zw\n\nEdcar Properties Team\n"Connecting People with Properties"'
        )
        mail.send(msg)
    except Exception as e:
        print(f'Email error: {e}')
