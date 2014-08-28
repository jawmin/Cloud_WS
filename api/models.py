__author__ = 'benoit'

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Bundle(db.Model):
    __tablename__ = 'bundle'

    id_bundle = db.Column(db.String(), primary_key=True, nullable=False)
    id_user = db.Column(db.String(), nullable=False)
    services = db.relationship('Service', backref='bundle', lazy='dynamic', cascade='all, delete, delete-orphan')
    data = db.Column(db.String())

    def __init__(self, id_bundle, id_user, data):
        self.id_bundle = id_bundle
        self.id_user = id_user
        self.data = data

    def __repr__(self):
        return "<Bundle (id_bundle='%s', id_user='%s', data='%s')>" % (self.id_bundle, self.id_user, self.data)

    @classmethod
    def by_id(cls, bundle_id):
        return db.session.query(cls).filter(cls.id_bundle == bundle_id).first()


class Service(db.Model):
    __tablename__ = 'service'

    id_service = db.Column(db.String(), primary_key=True, nullable=False)
    id_bundle = db.Column(db.String(), db.ForeignKey("bundle.id_bundle"), nullable=False)
    num_units = db.Column(db.Integer(), nullable=False)

    def __init__(self, id_service, id_bundle, num_units):
        self.id_service = id_service
        self.id_bundle = id_bundle
        self.num_units = num_units

    def __repr__(self):
        return "<Service (id_service='%s', id_bundle='%s', num_units='%s')>" \
               % (self.id_service, self.id_bundle, self.num_units)


def init_db(app):
    db.init_app(app)
    return app