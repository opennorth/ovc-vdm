from datetime import datetime
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from flask.ext.restful import reqparse, Resource, inputs
from sqlalchemy.sql import func
from flask import Flask, render_template, request, abort
import os
import sendgrid
import mandrill


app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])

class unaccent(ReturnTypeFromArgs):
    pass


def send_mail(subject, msg, to=app.config['ADMINS'], sender=app.config['EMAIL_SENDER']):

    if app.config['SENDMAIL'] == True:
        try:
            mandrill_client = mandrill.Mandrill(app.config['EMAIL_CREDENTIALS'])

            message = {
                'from_email': sender,
                'from_name': 'Vue sur les contrats',
                'to': [{'email': app.config['ADMINS'][0],
                         'type': 'to'}],
                'subject': subject,
                'signing_domain': 'ville.montreal.qc.ca',
                'text': msg

            }

            result = mandrill_client.messages.send(message=message, async=False)
            print result    

        except mandrill.Error, e:
            app.logger.error("Mandrill error: %s" %  repr(e))
