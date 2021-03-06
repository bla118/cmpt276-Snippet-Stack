#####################################################################
############ THESE FUNCTIONS HAVE ALL BEEN TESTED ###################
#####################################################################

import sqlite3

# returns the name of the likes table of a comment
def generate_likes_table_name(snippet_id, comment_id):
    # the name of the likes table
    return "sc_" + str(snippet_id) + "_" + str(comment_id)

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
            cursor.execute(f'''INSERT INTO {snippet_id} (contents, likes, user_id) VALUES (?, 0, ?);''', 
                            insert_data)
        except:
            return False

        return True

# updates the contents of a comment
# returns true on success
def update_comment_of_snippet(snippet_id, comment_id, contents):
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()

        try:
            # update content of a comment
            cursor.execute(f'''UPDATE {snippet_id} SET contents = ? WHERE reply_id = ?;''', 
                            [contents, comment_id])
        except:
            return False

        return True


# returns all the comments to a snippet
def get_comments_for_snippet(snippet_id):
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()

        try:
            comments = cursor.execute(f'''SELECT * FROM {snippet_id};''').fetchall()
        except:
            return None

        return comments


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
            likes_table_name = generate_likes_table_name(snippet_id, like[0])
            cursor.execute(f'''DROP TABLE IF EXISTS {likes_table_name};''')

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
        likes_table_name = generate_likes_table_name(snippet_id, comment_id)
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {likes_table_name} 
                        (user_id text PRIMARY KEY UNIQUE NOT NULL) WITHOUT ROWID;''')

        # insert user_id into likes table
        try:
            cursor.execute(f'''INSERT INTO {likes_table_name} VALUES (?);''', 
                          [user_id])
        except:
            return False

        # increment the likes counter
        num_likes = cursor.execute(f'''SELECT likes FROM {snippet_id} WHERE reply_id = ?;''', 
                                    [comment_id]).fetchone()[0]
        cursor.execute(f'''UPDATE {snippet_id} SET likes = ? WHERE reply_id = ?;''', 
                        [num_likes + 1, comment_id])
        return True

def delete_likes_to_a_comment(snippet_id, comment_id, user_id):
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        # delete the user from the likes table
        likes_table_name = generate_likes_table_name(snippet_id, comment_id)
        try:
            cursor.execute(f'''DELETE FROM {likes_table_name} WHERE user_id = ?;''', [user_id])
        except:
            return

        # decrement the likes counter
        num_likes = cursor.execute(f'''SELECT likes FROM {snippet_id} WHERE reply_id = ?;''', 
                                    [comment_id]).fetchone()[0]
        cursor.execute(f'''UPDATE {snippet_id} SET likes = ? WHERE reply_id = ?;''', 
                        [num_likes - 1, comment_id])


######################## TEST FUNCTIONS ################################
# tests the above functions
# set display=True for debugging
def test_insert_likes_and_delete_comments_for_snippet(display=False):
    import random
    import string

    # a random snippet id
    snippet_id = "s_122"

    # letters A-Z
    USERS = ["User"+chr(i) for i in range(ord('A'), ord('Z') + 1)]

    # comments
    COMMENTS = []

    # test inserting many users
    for user_id in USERS:
        letters = string.ascii_letters
        comment = "<p>" + ''.join(random.choice(letters) for i in range(10)) + "</p>"
        COMMENTS.append(comment)

        insert_comments_for_snippet(snippet_id, (comment, user_id))

    # test get_comments
    if (display):
        results = get_comments_for_snippet(snippet_id)
        for i in results:
            print(i)

    # check if values are correct
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        data = cursor.execute(f'''SELECT * FROM {snippet_id} WHERE reply_id = 1;''').fetchall()
        fail = False
        for i in range(len(data)):
            d = data[i]
            
            if not (COMMENTS[i] == d[1] and USERS[i] == d[3]):
                fail = True
                if display:
                    print("failed:", d)

        if fail:
            print("INSERT FAILED.")
        else:
            print("INSERT PASSED.")


    # test updating reply contents
    comment_id = random.randint(0, len(USERS) - 1)
    contents = "<pre><code>print(\"hello\")</code></pre>"

    res = update_comment_of_snippet(snippet_id, comment_id, contents)
    if res: 
        print("UPDATE PASSED.")
    else:
        print("UPDATE FAILED.")

    if (display):
        print("Expected contents:", contents)
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            results = cursor.execute(f'''SELECT contents FROM {snippet_id} WHERE reply_id = ?;''',
                                        [comment_id]).fetchone()[0]
            print("Actual contents:", results)

    # test incrementing likes
    idx = random.randint(0, len(USERS) - 1)
    reply_id = idx + 1
    user_who_is_liked = USERS[idx]

    # everyone likes 'user_who_is_liked'
    for user_who_liked in USERS:
        if user_who_liked != user_who_is_liked:
            add_likes_to_a_comment(snippet_id, reply_id, user_who_liked)

    if (display):
        print("user who is liked:", user_who_is_liked)
        print("users that clicked like (below):")
        with sqlite3.connect('Snippets.db') as conn:
            cursor = conn.cursor()
            likes_table_name = generate_likes_table_name(snippet_id, reply_id)
            results = cursor.execute(f'''SELECT * FROM {likes_table_name};''').fetchall()
            for i in results:
                print(i)
            print("expected number of likes:", len(USERS) - 1)
            print("actual number of likes:", len(results))
        
    with sqlite3.connect('Snippets.db') as conn:
        cursor = conn.cursor()
        n = cursor.execute(f'''SELECT likes FROM {snippet_id} WHERE reply_id = ?;''', [reply_id]).fetchone()
        
        if int(n[0]) == len(USERS) - 1:
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
