# web_app/models.py

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Company_Info(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Company_Name = db.Column(db.String(128))
    Company_Ticker = db.Column(db.String(128))
    Sector = db.Column(db.String(128))
    SubIndustry = db.Column(db.String(128))
    HQ_Location = db.Column(db.String(128))
    Date_first_added_to_SP500 = db.Column(db.String(128))
    Founded = db.Column(db.Integer)


    def __repr__(self):
        return f"<Company_Info {self.Company_Ticker} {self.Company_Name}>"



def parse_records(database_records):
    """
    A helper method for converting a list of database record objects into a list of dictionaries, so they can be returned as JSON

    Param: database_records (a list of db.Model instances)

    Example: parse_records(User.query.all())

    Returns: a list of dictionaries, each corresponding to a record, like...
        [
            {"id": 1, "title": "Book 1"},
            {"id": 2, "title": "Book 2"},
            {"id": 3, "title": "Book 3"},
        ]
    """
    parsed_records = []
    for record in database_records:
        print(record)
        parsed_record = record.__dict__
        del parsed_record["_sa_instance_state"]
        parsed_records.append(parsed_record)
    return parsed_records