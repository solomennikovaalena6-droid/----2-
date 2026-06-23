# 🏦 Баркас Банк — Финансовый трекер

Веб-приложение для учёта доходов и расходов с авторизацией, CRUD операциями и REST API.

## 🚀 Технологии

- **Backend**: Flask 2.3.3, SQLAlchemy, WTForms, bcrypt
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Fetch API)
- **Auth**: Сессии, хэширование паролей

## 📦 Установка и запуск

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/your-username/barkas-bank.git
cd barkas-bank

# 2. Создайте виртуальное окружение
python -m venv venv

# 3. Активируйте его
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 4. Установите зависимости
pip install -r requirements.txt

# 5. Создайте файл .env
echo SECRET_KEY=your-secret-key-here > .env

# 6. Запустите приложение
python app.py