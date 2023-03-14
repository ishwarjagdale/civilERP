import datetime
import uuid

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID

db = SQLAlchemy()


class Contracts(db.Model):
    __table_name__ = "contracts"

    contract_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date_created = db.Column(db.TIMESTAMP, nullable=False, default=datetime.datetime.now)
    completed = db.Column(db.BOOLEAN, nullable=False, default=False)
    assigned_to = db.Column(UUID(as_uuid=True), db.ForeignKey('users.user_id'))


class ClientDetails(db.Model):
    __table_name__ = "client_details"

    contract_id = db.Column(UUID(as_uuid=True), db.ForeignKey('contracts.contract_id'), primary_key=True)
    name = db.Column(db.VARCHAR, nullable=False)
    contact = db.Column(db.VARCHAR, nullable=False)


class ContractDetails(db.Model):
    __table_name__ = "contract_details"

    contract_id = db.Column(UUID(as_uuid=True), db.ForeignKey('contracts.contract_id'), primary_key=True)
    delivers_name = db.Column(db.VARCHAR, nullable=False)
    recv_date = db.Column(db.TIMESTAMP, nullable=False, default=datetime.datetime.now)
    quantity = db.Column(db.INTEGER, nullable=False)
    condition = db.Column(db.VARCHAR, nullable=False)
    description = db.Column(db.VARCHAR, nullable=False)
    test_to_perform = db.Column(UUID(as_uuid=True), db.ForeignKey('tests.test_id'))


class Inventory(db.Model):
    __table_name__ = "inventory"

    item_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contract_id = db.Column(UUID(as_uuid=True), db.ForeignKey('contracts.contract_id'))
    original_id_mark = db.Column(db.VARCHAR)
    sample_code = db.Column(db.VARCHAR)
    test_results = db.Column(db.VARCHAR)


class Tests(db.Model):
    __table_name__ = "tests"

    test_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    test_name = db.Column(db.VARCHAR, nullable=False)
    test_attrib = db.Column(db.VARCHAR, nullable=False, default="Value")


class Users(db.Model):
    __table_name__ = "users"

    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.VARCHAR, nullable=False)
    email_address = db.Column(db.VARCHAR, nullable=False, unique=True)
    password = db.Column(db.VARCHAR, nullable=False)
    date_joined = db.Column(db.TIMESTAMP, nullable=False, default=datetime.datetime.now)
    authenticated = db.Column(db.BOOLEAN, nullable=False, default=False)
    superuser = db.Column(db.BOOLEAN, nullable=False, default=False)
    active = db.Column(db.BOOLEAN, nullable=False, default=True)

    @property
    def is_authenticated(self):
        return self.authenticated

    @property
    def is_superuser(self):
        return self.superuser

    @property
    def is_active(self):
        return self.active

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.user_id)

    def __eq__(self, other):
        if isinstance(other, Users):
            return self.get_id() == other.get_id()

    def __ne__(self, other):
        return not self.__eq__(other)

    @staticmethod
    def get(user_id):
        return Users.query.filter_by(user_id=user_id).first()

    @staticmethod
    def get_by_email(email):
        return Users.query.filter_by(email_address=email).first()

    @staticmethod
    def create_super_user():
        if not Users.query.filter_by(superuser=True).first():
            user = Users(name="admin", email_address="admin@noorg.org", password="admin1234", superuser=True,
                         authenticated=True)
            db.session.add(user)
            db.session.commit()

