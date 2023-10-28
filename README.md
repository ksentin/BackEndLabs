# Lab1BackEnd
## Як запустити проект локально

1. **Клонуйте репозиторій**

    ```bash
    git clone https://github.com/ksentin/Lab1BackEnd.git
    cd Lab1BackEnd
    ```
2. **Встановіть віртуальне середовище**

    ```bash
    python3 -m venv env
    source ./env/bin/activate
    ```
3. **Встановіть залежності**

    ```bash
    pip install -r requirements.txt
    ```
4. **Запустіть застосунок**

    ```bash
    flask run --host 0.0.0.0 -p 5004
    ```
5. **Перевірте ендпоінт `/healthcheck`**

    Перейдіть за адресою `http://0.0.0.0:5004/healthcheck`. Ви повинні отримати відповідь з кодом 200 та JSON-об'єктом, який містить поточну дату та статус сервісу.

## Використання Docker

Якщо у вас встановлено Docker, ви можете використати його для запуску застосунку.

1. **Збудуйте Docker image**

    ```bash
    docker build --build-arg PORT=5005 . -t myapp:latest
    ```

2. **Запустіть Docker контейнер**

    ```bash
    docker run -it --rm --network=host myapp:latest
    ```

    Тепер застосунок повинен бути доступний на `http://127.0.0.1:5004`.

## Посилання на задеплоєний проект:
https://backend2-kwlg.onrender.com

   


   
       
