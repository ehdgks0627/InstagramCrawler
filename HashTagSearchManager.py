from HashTagSearch import HashTagSearch
import sqlite3


class HashTagSearchManager(HashTagSearch):
    def __init__(self):
        super().__init__()
        self.total_posts = 0
        self.conn = sqlite3.connect("database.sqlite3")
        self.cur = self.conn.cursor()
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Image (
                            path VARCHAR(256),
                            tag VARCHAR(256),
                            post_id VARCHAR(256))""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Post (
                            post_id VARCHAR(256), 
                            code VARCHAR(256), 
                            caption VARCHAR(256),
                            user VARCHAR(256), 
                            display_src VARCHAR(256), 
                            is_video VARCHAR(256), 
                            created_at VARCHAR(256))""")
        self.conn.commit()

    def __del__(self):
        self.conn.close()

    def save_results(self, instagram_results):
        super().save_results(instagram_results)
        sql = "INSERT INTO Post VALUES (?, ?, ?, ?, ?, ?, ?)"
        datas = []

        for i, post in enumerate(instagram_results):
            datas.append((str(post.post_id),
                          str(post.code),
                          str(post.caption),
                          str(post.user),
                          str(post.display_src),
                          str(post.is_video),
                          str(post.created_at)))

        self.cur.executemany(sql, datas)
        self.total_posts += len(datas)
        print("[Total Post - %d] %d - Post Inserted" % (self.total_posts, len(datas)))
        # TODO(sprout): save image
