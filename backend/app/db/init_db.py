from .base import transaction
from .tables import CREATE_INDEX_STATEMENTS, CREATE_TABLE_STATEMENTS


def init_db():
    with transaction() as connection:
        for statement in CREATE_TABLE_STATEMENTS:
            connection.execute(statement)
        for statement in CREATE_INDEX_STATEMENTS:
            connection.execute(statement)
