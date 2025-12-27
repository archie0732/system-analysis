import sqlite3
import os


class LibraryDB:
    def __init__(self, db_name="library.db"):
        self.db_name = db_name
        self.init_db()

    def connect(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        """建立資料庫結構與假資料"""
        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """CREATE TABLE IF NOT EXISTS books
                          (id INTEGER PRIMARY KEY, title TEXT, status TEXT)"""
        )
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS users
                          (id INTEGER PRIMARY KEY, name TEXT, borrowed_count INTEGER)"""
        )

        cursor.execute("SELECT count(*) FROM books")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO books VALUES (101, '系統分析', 'Available')")
            cursor.execute(
                "INSERT INTO books VALUES (102, 'Python程式設計', 'Borrowed')"
            )
            cursor.execute("INSERT INTO users VALUES (411211480, '許育祁', 0)")
            conn.commit()
            print("[DB Init] 資料庫已建立並寫入初始資料。")

        conn.close()

    def get_user_info(self, user_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT name, borrowed_count FROM users WHERE id=?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def check_book_status(self, book_id):
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute("SELECT status, title FROM books WHERE id=?", (book_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def update_book_status(self, book_id, new_status):
        conn = self.connect()
        conn.cursor().execute(
            "UPDATE books SET status=? WHERE id=?", (new_status, book_id)
        )
        conn.commit()
        conn.close()

    def update_user_count(self, user_id, new_count):
        conn = self.connect()
        conn.cursor().execute(
            "UPDATE users SET borrowed_count=? WHERE id=?", (new_count, user_id)
        )
        conn.commit()
        conn.close()


class BorrowSystem:
    def __init__(self):
        self.db = LibraryDB()

    def check_permission(self, user_id):
        print(f"   [系統] 檢查使用者 {user_id} 權限中...")
        user_data = self.db.get_user_info(user_id)

        if user_data:
            name, count = user_data
            print(f"   [DB回傳] 姓名: {name}, 目前借閱數: {count}")

            if count < 5:
                print("   [結果] 權限通過 (Allow)")
                return True, count
            else:
                print("   [結果] 權限拒絕 (Deny) - 已達借閱上限！")
                return False, count
        else:
            print("   [錯誤] 找不到使用者")
            return False, 0

    def borrow_book(self, user_id, book_id):
        print(f"\n====== 執行借書 Request (User: {user_id}, Book: {book_id}) ======")

        allowed, current_count = self.check_permission(user_id)

        if allowed:
            book_data = self.db.check_book_status(book_id)
            if book_data:
                status, title = book_data
                if status == "Available":
                    self.db.update_book_status(book_id, "Borrowed")
                    self.db.update_user_count(user_id, current_count + 1)
                    print(f"====== 成功！書籍 '{title}' 借閱完成 ======")
                else:
                    print(f"====== 失敗：書籍 '{title}' 已被借出 ======")
            else:
                print("====== 失敗：書籍不存在 ======")
        else:
            print("====== 失敗：權限不足，操作取消 ======")


if __name__ == "__main__":
    db_file = "library.db"
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"--- 舊的 {db_file} 已刪除，環境重置完成 ---")
        except PermissionError:
            print(f"!!! 錯誤：無法刪除 {db_file}，請先關閉 DB Browser 軟體 !!!")
            exit()

    system = BorrowSystem()
    my_id = 411211480

    print("\n\n>>> 測試情境 A: 正常借書 (Happy Path)")
    system.borrow_book(my_id, 101)
    print("\n\n>>> 測試情境 A: 重複借書")
    system.borrow_book(my_id, 101)
    print("\n\n>>> 測試情境 C: 模擬借閱額度已滿 (Exception Path)")
    system.db.update_user_count(my_id, 5)

    system.borrow_book(my_id, 102)
