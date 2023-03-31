


# class Database:
#     def __init__(self, db_file):
#         self.connection = sqlite3.connect(db_file)
#         self.cursor = self.connection.cursor()
#
#     def exist_user(self, user_id):
#         with self.connection:
#             res = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id, )).fetchall()
#             return bool(len(res))
#
#     def add(self, user_id):
#         with self.connection:
#             return self.connection.execute("INSERT INTO users ('user_id') VALUES (?)", (user_id,))
#
#     def mute(self, user_id):
#         with self.connection:
#             user = self.connection.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
#             return user[5] == 1
#
#     def add_mute(self, user_id, is_mute=1):
#         return self.connection.execute("UPDATE users SET moderator_username = ? WHERE user_id = ?",
#         (is_mute, user_id))
#
#     def unmute(self, user_id, is_muted=''):
#         with self.connection:
#             lifes = self.cursor.execute("SELECT lifes FROM users WHERE user_id = ?", (user_id,)).fetchone()
#             print(lifes[0])
#         return (
#             (self.connection.execute("UPDATE users SET is_muted = ? WHERE user_id = ?", (is_muted, user_id))),
#             (self.connection.execute("UPDATE users SET lifes = ? WHERE user_id = ?", (lifes[0]-1, user_id)))
#         )
