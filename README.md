# Product Categories API

Пример проекта по ТЗ: управление товарами, категориями и заказами.

### ТЗ:
### 1. "Написать даталогическую схему данных"
 - Даталогическая схема данных реализована в разделе models и включает основные сущности: категории товаров с иерархией (Category и CategoryClosure), товары (Product), клиентов (Client), заказы (Order) и позиции заказов (OrderItem). Она позволяет хранить категории с неограниченным уровнем вложенности и выполнять все необходимые операции, предусмотренные ТЗ

### 2. "Написать соответствующие SQL запросы для работы с базой"
#### 2.1 Получение информации о сумме товаров заказанных под каждого клиента (Наименование клиента, сумма)
```
SELECT 
    c.name AS client_name,
    SUM(oi.qty * oi.unit_price) AS total_amount
FROM client c
JOIN orders o ON c.id = o.client_id
JOIN order_item oi ON o.id = oi.order_id
GROUP BY c.id, c.name
```
#### 2.2 Найти количество дочерних элементов первого уровня вложенности для категорий номенклатуры.
```
SELECT 
    c.id AS category_id,
    c.name AS category_name,
    COUNT(ch.id) AS first_level_children_count
FROM category c
LEFT JOIN category ch ON ch.parent_id = c.id
GROUP BY c.id, c.name
ORDER BY first_level_children_count DESC;
```
#### 2.3.1. Написать текст запроса для отчета (view) «Топ-5 самых покупаемых товаров за последний месяц» (по количеству штук в заказах). В отчете должны быть: Наименование товара, Категория 1-го уровня, Общее количество проданных штук.
```
WITH last_month_orders AS (
    SELECT oi.product_id, oi.qty
    FROM order_item oi
    JOIN orders o ON oi.order_id = o.id
    WHERE o.created_at >= date_trunc('month', current_date) - INTERVAL '1 month'
      AND o.created_at < date_trunc('month', current_date)
)
SELECT 
    p.name AS product_name,
    c_root.name AS root_category_name,
    SUM(lm.qty) AS total_sold_qty
FROM last_month_orders lm
JOIN product p ON lm.product_id = p.id
JOIN category c ON p.category_id = c.id
JOIN category c_root ON COALESCE(p.root_category_id, c.id) = c_root.id
GROUP BY p.id, p.name, c_root.name
ORDER BY total_sold_qty DESC
LIMIT 5;
```
#### 2.3.2. Проанализировать написанный в п. 2.3.1 запрос и структуру БД. Предложить варианты оптимизации этого запроса и общей схемы данных для повышения производительности системы в условиях роста данных (тысячи заказов в день).
```
Индексы:
orders.created_at - для быстрого фильтра по дате.
order_item.order_id - для соединения с orders.
product.id - для соединения с order_item.
product.root_category_id - чтобы ускорить поиск категории первого уровня.
Хранение root_category_id уже есть, что избавляет от рекурсивного запроса к CategoryClosure.
```

### 3. "Написать сервис «Добавление товара в заказ»...
...который работает по REST-API. Метод должен принимать ID заказа, ID номенклатуры и количество. Если товар уже есть в заказе, его количество должно увеличиваться, а не создаваться новая позиция. Если товара нет в наличии то должна возвращаться соответствующая ошибка. Стек -  любой фреймворк в пределах Python. Git репозиторий, контейнеризация, документация, и прочее — приветствуется."

### Реализовано:
- REST-API сервис для добавления товара в заказ (/orders/add-item).
- Если товар уже есть в заказе, его количество увеличивается.
- Если товара нет в наличии, возвращается ошибка 409.
- Если заказа или товара нет, возвращается ошибка 404.

- Реляционная схема данных для хранения:
  - Товары (Product) с количеством и ценой
  - Категории товаров с неограниченной вложенностью (Tree/Closure Table)
  - Клиенты (Client)
  - Заказы и позиции в заказе (Order и OrderItem)

- Возможность легко получать вложенные категории для построения дерева товаров.
- Полная асинхронная реализация с FastAPI + SQLAlchemy + asyncpg.
- Контейнеризация через Docker и docker-compose.


## Стек
- Python 3.11, FastAPI
- PostgreSQL
- SQLAlchemy (async)
- Alembic
- Docker + docker-compose

## Запуск проекта
#### 1. Клонирование репозитория
```
git clone https://github.com/Dopelen/Product_categories
cd Product_categories
```

#### 2. Сборка контейнера
```bash
docker-compose up --build -d
```

#### 3. Создаем первую миграцию для создания таблиц по схемам проекта
```bash
docker exec -it product_categories-app-1 sh -c "poetry run alembic revision --autogenerate -m 'initial tables'"
```

#### 4. Применяем миграцию
```bash
docker exec -it product_categories-app-1 sh -c "poetry run alembic upgrade head"
```

NOTE: С этого момента приложение полноценно работает, осталось добавить тестовые данные на которых можно было бы провести проверку

#### 5. Добавление тестовых данных 
Можно подключиться к базе напрямую через pgAdmin или произвести ввод подключившись к контейнеру
```bash
docker exec -it product_categories-db-1 psql -U postgres -d product_categories
```

```
INSERT INTO client (id, name, address) VALUES (1, 'Client A', 'Street 1');
INSERT INTO category (id, name, parent_id) VALUES (1, 'Electronics', NULL);
INSERT INTO product (id, name, category_id, qty, price, root_category_id) VALUES
(1, 'iPhone 15', 1, 10, 999.99, 1);
INSERT INTO orders (id, client_id) VALUES (1, 1);
```
#### 6. Тестирование API
Тестирование можно провести через Swagger UI после запуска контейнера по адресу: http://localhost:8000/docs

P.S: Я намеренно оставил пример .env файла с "значениями по умолчанию" для простоты запуска

#### 7. Последние изменения
- Изменил систему управления переменными окружения на config файл с использование Pydantic и генерацией строки подключения к базе данных
- Оптимизировал docker файл, убрав лишние зависимости системы
- Оптимизировал docker-compose файл: пробросил порты БД для подключения, добавил healthcheck при запуске для корректного старта приложения, изменил env переменные с хардкода на доступ через файл переменных
- Изменил базовый файл alembic.ini для читаемости
- Изменил alembic env файл добавив строку подключения через config file
- Вынес инициирующую миграцию из контейнера, оставив внутри только команду применения миграция, без их создания
- Теперь при сборке миграция применяется автоматически, а инициирующая находится изначально в репозитории
- Добавил скрипт добавления тестовых данных
