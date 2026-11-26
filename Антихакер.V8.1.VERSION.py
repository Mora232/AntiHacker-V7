import os
import sys
import time
import bcrypt
import hashlib
import sqlite3

DB_FILE = 'security.db'
ET_TXT = 'etalon.txt'
PS_TXT = 'etalon_log.txt'
MAX_ATTEMPTS = 3

time_start = time.perf_counter()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    return conn, cursor

def get_hash_file(filename):
    with open(filename, 'rb') as file:
        return hashlib.sha256(file.read()).hexdigest()

def chech_file():
    try:
        with open(ET_TXT, "r") as file:
            ET_HASH = file.read().strip()
        FR_HASH = get_hash_file(DB_FILE)
        if FR_HASH != ET_HASH:
            print("ошибка при проверке...")
            sys.exit(1)
    except FileNotFoundError:
        print("файл не найден...")
        sys.exit(1)

def conn_sql():
    conn, cursor = get_db()
    cursor.execute('SELECT is_banned FROM blacklist WHERE is_banned = 1')
    ban_record = cursor.fetchone()
    conn.close()
    if ban_record and ban_record[0]:
        print('Вы заблокированы...')
        os._exit(1)

def passw_hash():
    conn, cursor = get_db()
    cursor.execute('SELECT password_hash FROM users LIMIT 1')
    db_hash = cursor.fetchone()[0]
    conn.close()
    return db_hash

def ban_list():
    conn, cursor = get_db()
    cursor.execute("INSERT INTO blacklist(is_banned) VALUES (1)")
    conn.commit()
    conn.close()
    new_hash = get_hash_file(DB_FILE)
    with open(ET_TXT, "w") as file:
        file.write(new_hash)

def password_check():
    attempts = 0
    while True:
        try:
            user_input = input('Введите пароль: ').encode('utf-8')
            if bcrypt.checkpw(user_input, passw_hash()):
                if os.path.exists(PS_TXT): os.remove(PS_TXT)
                print('Вход разрешен')
                break
        except KeyboardInterrupt:
            print('Обнаружена попытка взлома. Блокировка...')
            ban_list()
            os._exit(1)
        else:
            try:
                with open(PS_TXT, 'r') as file:
                    digit = int(file.read().strip())
                    if 0 < digit:
                        attempts = digit
            except FileNotFoundError:
                pass
            attempts += 1
            if attempts >= MAX_ATTEMPTS:
                print('Обнаружена попытка взлома. Блокировка...')
                ban_list()
                os._exit(1)
            else:
                with open(PS_TXT, 'w') as file:
                    file.write(f'{attempts}')
                    print(f"Пароль введен неверно, осталось {MAX_ATTEMPTS - attempts} попыток")
chech_file()
conn_sql()
password_check()
time_end = time.perf_counter()
print(f"время сессии: {time_end - time_start}")