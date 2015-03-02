from datetime import datetime
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from flask.ext.restful import reqparse, Resource, inputs
from sqlalchemy.sql import func
from flask import Flask, render_template, request, abort


class unaccent(ReturnTypeFromArgs):
    pass

