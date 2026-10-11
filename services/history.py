import sqlite3

DATABASE = "database/vedfinder.db"


def save_history(username, query):

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute(

        """

        INSERT INTO history

        (username,query)

        VALUES(?,?)

        """,

        (

            username,

            query

        )

    )

    conn.commit()

    conn.close()


def get_history(username):

    conn = sqlite3.connect(DATABASE)

    cur = conn.cursor()

    cur.execute(

        """

        SELECT query

        FROM history

        WHERE username=?

        ORDER BY id DESC

        LIMIT 20

        """,

        (username,)

    )

    rows = cur.fetchall()

    conn.close()

    return [row[0] for row in rows]