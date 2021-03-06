import sqlite3

############# REPLIES TABLE ###############
# table: <snippet_id>                     #
#                                         #
#+----------+----------+-------+---------+#
#| reply_id | contents | likes | user_id |#
#+----------+----------+-------+---------+#
#| 1        | "hello"  |   3   | stalin4 |#
#| 2        | "cool"   |   0   | hitler4 |#
###########################################

# creates the table above
# inserts comments to the above table
# returns true if successful
# example: insert_comments_for_snippet("s_2222", (contents, user_id))
def insert_comments_for_snippet(snippet_id, insert_data):
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        # create table if table does not exist
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {snippet_id} (reply_id INTEGER PRIMARY KEY, 
                                                contents text NOT NULL, 
                                                likes integer NOT NULL, 
                                                user_id text NOT NULL);''')

        try:
            # insert values
            cursor.execute(f'''INSERT INTO {snippet_id} (contents, likes, user_id) VALUES (?, 0, ?);''', insert_data)
        except:
            return False

        return True

# only deletes all the comments to a snippet
# does not delete the snippet itself
# call this when the snippet owner deletes snippet
def delete_comments_for_snippet(snippet_id):
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        # delete table if table does exists
        likes = cursor.execute(f'''SELECT reply_id FROM {snippet_id};''').fetchall()

        # delete the likes of all comments
        for like in likes:
            name = "sc_" + str(snippet_id) + "_" + str(like[0])
            cursor.execute(f'''DROP TABLE IF EXISTS {name};''')

        # drop the replies table
        cursor.execute(f'''DROP TABLE IF EXISTS {snippet_id};''').fetchall()


################ LIKES TABLE ##############
# likes table: sc_<snippet_id><comment_id>#
#                                         #
#+---------------------------------------+#
#|               user_id                 |#
#+---------------------------------------+#
#|               stalin4                 |#
#+---------------------------------------+#
#|               hitler4                 |#
###########################################

# increments the likes counter for a comment NOT a snippet
# returns true if successful
# example: add_likes_to_a_comment("s_1111", "123", "stalin4") -> true
#          add_likes_to_a_comment("s_1111", "123", "stalin4") -> false
def add_likes_to_a_comment(snippet_id, comment_id, user_id):
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        # create likes table that contains all user_id's that liked the post
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {"sc_" + str(snippet_id) + "_" + str(comment_id)} 
                        (user_id text PRIMARY KEY UNIQUE NOT NULL) WITHOUT ROWID;''')

        # insert user_id
        try:
            cursor.execute(f'''INSERT INTO {"sc_" + str(snippet_id) + "_" + str(comment_id)} VALUES (?);''', 
                          [user_id])
        except:
            return False

        # increment the likes counter
        num_likes = cursor.execute(f'''SELECT likes FROM {snippet_id} WHERE reply_id = ?;''', 
                                    [comment_id]).fetchone()[0]
        cursor.execute(f'''UPDATE {snippet_id} SET likes = ?;''', [num_likes + 1])
        return True



######################## TEST FUNCTIONS ################################
# tests the above 2 functions
# set display=True for debugging
def test_insert_likes_and_delete_comments_for_snippet(display=True):
    snippet_id = "s_122"

    user_id = "admin"
    comment = "<pre><code>print(\"hello\")</pre></code>"
    # test inserting
    insert_comments_for_snippet(snippet_id, (comment, user_id))

    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        data = cursor.execute(f'''SELECT * FROM {snippet_id} WHERE reply_id = 1;''').fetchone()
        if display:
            print("reply_id:", data[0])
            print("contents:", data[1])
            print("likes:", data[2])
            print("user_id:", data[3])
        
        if comment == data[1] and user_id == data[3]:
            print("INSERT PASSED.")
        else:
            print("INSERT FAILED.")

    # test incrementing likes
    reply_id = data[0]
    user_who_liked = "stalin1000"
    add_likes_to_a_comment(snippet_id, reply_id, user_who_liked)

    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        u = cursor.execute(f'''SELECT * FROM {"sc_" + str(snippet_id) + "_" + str(reply_id)};''').fetchone()
        n = cursor.execute(f'''SELECT likes FROM {snippet_id} WHERE reply_id = ?;''', [reply_id]).fetchone()

        if display:
            print("user who liked:", u[0])
            print("like counter:", n[0])
        
        if int(n[0]) == int(data[2]) + 1:
            print("INCREMENT LIKES COUNTER PASSED.")
        else:
            print("INCREMENT LIKES COUNTER FAILED.")

    # test deleting
    delete_comments_for_snippet(snippet_id)

    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f'''SELECT * FROM {snippet_id} WHERE reply_id = 1;''').fetchone()
            print("DELETE FAILED.")
        except:
            print("DELETE PASSED.")


    # clear the test tables
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f'''DROP TABLE IF EXISTS {snippet_id};''')
