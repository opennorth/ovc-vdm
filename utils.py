from datetime import datetime
from sqlalchemy.sql.functions import ReturnTypeFromArgs

def date_time_arg (value):

    #TODO SEE how to reject if not format YYYY-MM-DD (regex dans agg_argument!!)
    return datetime.strptime(value, "%Y-%m-%d") 


class unaccent(ReturnTypeFromArgs):
    pass

