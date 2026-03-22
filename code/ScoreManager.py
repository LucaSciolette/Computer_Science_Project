import sqlite3


class ScoreManager:

    def __init__(self,database):
        self.database = database
        self.create_table()

    def create_table(self):

        ''' here im creating the high score table if it doesn't already exist
            I'm saying the difficulty is an integer easy is 1 medium is 2 and so on
            I am also limiting the length of the player name.
            I could use player name and high score as composite primary key but same player could get same score
        '''

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS high_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name VARCHAR(5) NOT NULL,
                    difficulty INTEGER NOT NULL, 
                    score INTEGER NOT NULL
                )
            ''')

            conn.commit()

    def get_high_score(self,difficulty_num):
        '''Here I take a difficulty as a parameter and
        query from the database to
        find the highest score for the difficulty'''

        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT MAX(score) FROM high_scores WHERE difficulty = ?', (difficulty_num,))

            conn.commit()
            high_score = cursor.fetchall()

            # checking if the database is empty,
            # if so the high score returned is 0
            if high_score != [(None,)]:
                high_score = high_score[0][0]
            else:
                high_score = 0
            return high_score

    def get_player_name(self,difficulty_num):

        # same as get high score
        # but returning player name instead
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT MAX(score),player_name FROM high_scores WHERE difficulty = ?', (difficulty_num,))

            conn.commit()
            player_name = cursor.fetchall()
            if player_name[0][0] != None:
                player_name = player_name[0][1]
            else:
                player_name = ''
            return player_name

    def add_new_highscore(self,player_name,difficulty,score):
        '''Takes player name, difficulty and score as parameters
        to create a new entry in the high score table'''
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()

            cursor.execute('INSERT INTO high_scores (player_name, difficulty, score) VALUES(?,?,?)',(player_name,difficulty,score) )

            conn.commit()
