# Каталог — Flask MVP

## Запуск

```bash
python -m venv venv
source venv/bin/activate
# Windows: venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
python run.py
```

Откройте http://127.0.0.1:5000

По умолчанию администратор:
- логин: `admin`
- пароль: `admin123`

Перед production обязательно задайте `SECRET_KEY` и `ADMIN_PASSWORD` в `.env`.

## Основные URL

- `/login` — вход
- `/admin/` — админ-панель
- `/seller/` — кабинет продавца
- `/store/<slug>` — публичный каталог
- `/store/<slug>/cart` — корзина

## Архитектура

Flask Blueprints разделяют auth/admin/seller/catalog/cart. SQLAlchemy используется как ORM. Покупатель не регистрируется: корзина хранится в Flask session.

## Важное
URL магазина формируется из названия магазина, например:
`/store/my-shop` или `/store/moy-magazin`.
Если название совпадает, добавляется суффикс `-2`, `-3` и т.д.

В корзине:
- товары суммируются по количеству;
- `+` и `−` меняют количество;
- галочка выбирает товар для заказа;
- красный badge показывает общее количество единиц;
- WhatsApp-заказ содержит только выбранные позиции.
