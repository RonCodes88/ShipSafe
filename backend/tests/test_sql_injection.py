def get_user(id):
    query = "SELECT * FROM users WHERE id = " + id
    cursor.execute(query)
    return cursor.fetchall()