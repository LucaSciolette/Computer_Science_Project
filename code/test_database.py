from CSproject.code.ScoreManager import ScoreManager

import pytest

@pytest.fixture
def full_database():
    '''In this function I create a test database with
    testing values, I will be passing this database
    object through as a parameter into the other test
    functions'''
    db = ScoreManager('test.db')
    db.add_new_highscore('luca',1,500)
    db.add_new_highscore('mark',1,499)
    db.add_new_highscore('filip', 1, 500)
    db.add_new_highscore('david', 2, 100)
    return db

def test_get_player_name(full_database):
    '''this is to test the get_player_name function
    to see if it returns the correct name'''
    assert full_database.get_player_name(1) == 'luca'
    assert full_database.get_player_name(2) == 'david'

def test_get_highscore_name(full_database):
    '''this is to test the get_high_score function
        to see if it returns the score'''
    assert full_database.get_high_score(1) == 500
    assert full_database.get_high_score(2) == 100