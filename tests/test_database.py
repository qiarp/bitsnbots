import pytest
from storage.database import Database


@pytest.mark.Database
def test_setup_database():
    with Database() as db:
        print(db.log)

