import os
import bcrypt
import hashlib
import time
import sqlite3
time_start = time.perf_counter()
def get_hash_file(filename):
    with open(filename, "rb") as file:
        return hashlib.sha256(file.read()).hexdigest()
try:
    with open("etalon.txt", "r") as file:
        etalon_hash = file.read().strip()
    fresh_hash = get_hash_file("security.db")
    if fresh_hash != etalon_hash:
        print("пошел нахуй")
        os._exit(1)
except FileNotFoundError:
    print("пошел нахуй")
    os._exit(1)
conn = sqlite3.connect("security.db")
cursor = conn.cursor()
cursor.execute("SELECT is_banned FROM blacklist WHERE is_banned = 1")
ban_record = cursor.fetchone()
if ban_record and ban_record[0]:
    print("пошел нахуй")
    os._exit(1)
cursor.execute("SELECT password_hash FROM users LIMIT 1")
db_hash = cursor.fetchone()[0]
attempts = 0
while True:
    try:
        user_input = input("Введите пароль: ").encode("utf-8")
        if bcrypt.checkpw(user_input, db_hash):
            if not os.path.exists("etalon_log.txt"):
                pass
            else:
                os.remove("etalon_log.txt")
            print("Вход разрешен")
            break
    except KeyboardInterrupt:
        print("Обнаружена попытка взлома. Блокировка...")
        cursor.execute("INSERT INTO blacklist(is_banned) VALUES (1)")
        conn.commit()
        conn.close()
        new_hash = get_hash_file("security.db")
        with open("etalpn.txt", "w") as file:
            file.write(new_hash)
        os._exit(1)
    else:
        try:
            with open("etalon_log.txt", "r") as file:
                digit = int(file.read().strip())
                if 0 < digit:
                    attempts = digit
        except FileNotFoundError:
            pass
        attempts += 1
        if attempts >= 3:
            print("Обнаружена попытка взлома. Блокировка...")
            cursor.execute("INSERT INTO blacklist(is_banned) VALUES (1)")
            conn.commit()
            conn.close()
            new_hash = get_hash_file("security.db")
            with open("etalon.txt", "w") as file:
                file.write(new_hash)
            os._exit(1)
        else:
            with open("etalon_log.txt", "w") as file:
                file.write(f"{attempts}")
                print(f"Пароль введен неверно, осталось {3 - attempts} попыток")
time_end = time.perf_counter()
print(f"время сессии: {time_end - time_start}")