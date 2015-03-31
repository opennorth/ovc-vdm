from datetime import datetime
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from flask.ext.restful import reqparse, Resource, inputs
from sqlalchemy.sql import func
from flask import Flask, render_template, request, abort
import os
import sendgrid


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

class unaccent(ReturnTypeFromArgs):
    pass


def send_mail(subject, msg, to=app.config['ADMINS'], sender=app.config['EMAIL_SENDER']):
    sg = sendgrid.SendGridClient(app.config['EMAIL_CREDENTIALS'][0], app.config['EMAIL_CREDENTIALS'][1], )
    message = sendgrid.Mail()

    message.add_to(to)
    message.set_from(sender)
    message.set_subject(subject)
    message.set_text(msg)

    try:
        sg.send(message)
    except SendGridClientError as e:
        app.logger.error("SendGridClientError error: %s" %  repr(e))
    except SendGridServerError as e:
        app.logger.error("SendGridServerError error: %s" %  repr(e))

