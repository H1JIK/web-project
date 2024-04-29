import datetime
import sqlalchemy
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Score(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'estimation_txt'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    application_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    est_actual = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_purpose = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_validity = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_resonance = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_present_style = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_professionalism = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_feed_avail = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_materials_cycle = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_add = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_cliche = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_contract = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_gramm_errors = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)
    est_lexical_errors = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=False)

    # user_id = sqlalchemy.Column(sqlalchemy.Integer,
    #                            sqlalchemy.ForeignKey("users.id"))
    # user = orm.relation('User')
