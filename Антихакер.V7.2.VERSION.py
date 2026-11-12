import sqlite3
import bcrypt
import os
import time
import hashlib
start_time = time.perf_counter()
def get_file_hash(filename):
    with open(filename, 'rb') as file:
        return hashlib.sha256(file.read()).hexdigest()
try:
    with open('etalon.txt', 'r') as file:
        etalon_hash = file.read().strip()
    fresh_hash = get_file_hash('security.db')
    if fresh_hash != etalon_hash:
        print("Файл security.db был изменен. Доступ запрещен.")
        os._exit(1)
except FileNotFoundError:
    print('ФАЙЛ ОТСУТСТВУЕТ. ДОСТУП ЗАПРЕЩЕН.')
    os._exit(1)
if not os.path.exists('security.db'):
    print("[-] КРИТИЧЕСКАЯ УГРОЗА: База данных отсутствует!")
    os._exit(1)
conn = sqlite3.connect('security.db')
cursor = conn.cursor()
cursor.execute('SELECT is_banned FROM blacklist')
ban_record = cursor.fetchone()
if ban_record and ban_record[0] == 1:
    print("[-] ДОСТУП ЗАПРЕЩЕН. Вы были заблокированы навсегда.")
    os._exit(1)
cursor.execute('SELECT password_hash FROM users LIMIT 1')
db_hash = cursor.fetchone()[0]
attempts = 0
while True:
    try:
        user_input = input('Введите пароль: ').encode('utf-8')
        if bcrypt.checkpw(user_input, db_hash):
            print('Вход разрешен')
            break
    except KeyboardInterrupt:
            print('Обнаружена попытка взлома. Блокировка...')
            cursor.execute('INSERT INTO blacklist (is_banned) VALUES (1)')
            conn.commit()
            conn.close()
            new_hash = get_file_hash('security.db')
            with open('etalon.txt', 'w') as file:
                file.write(new_hash)
                os._exit(1)
    else:
        attempts += 1
        if attempts == 3:
            print('Обнаружена попытка взлома. Блокировка...')
            cursor.execute('INSERT INTO blacklist (is_banned) VALUES (1)')
            conn.commit()
            conn.close()
            new_hash = get_file_hash('security.db')
            with open('etalon.txt', 'w') as file:
                file.write(new_hash)
                os._exit(1)
        else:
            print(f'Пароль введен неверно, осталось попыток - {3 - attempts}')
end_time = time.perf_counter()
print(f'Время сессии = {end_time - start_time}')