# AI_olimp_2024

[![Black](https://github.com/Sashayerty/AI_olimp_2024/actions/workflows/black.yml/badge.svg?branch=main&event=push)](https://github.com/Sashayerty/AI_olimp_2024/actions/workflows/black.yml)
[![Flake8](https://github.com/Sashayerty/AI_olimp_2024/actions/workflows/flake8.yml/badge.svg?branch=main&event=push)](https://github.com/Sashayerty/AI_olimp_2024/actions/workflows/flake8.yml)  
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)

## ***[-Видео с демонстрацией функционала-](https://disk.yandex.ru/i/XjbH25PTdTH8xg)***

## Содержание

- [Список папок и файлов](#список-папок-и-файлов)
- [Пример `.env` файла](#пример-env-файла)
- [***Как запустить проект***](#как-запустить-проект)
- [Flask-admin, или как сделать выбор в сторону flask, а не django](#flask-admin-или-как-сделать-выбор-в-сторону-flask-а-не-django)
- [Данные для входа в админку](#данные-для-входа-в-админку)
- [Функция сильного/слабого сжатия текста пользователя/из бд](#функция-сильногослабого-сжатия-текста-пользователяиз-бд)

***Перед запуском проекта***, стоит позаботится о том, чтобы у Вас был API ключ от YandexConsole.  
Существует много инструкций на просторах Интернета, как это сделать. [Ссылка](https://console.yandex.cloud/) на YandexConsole.

## Список папок и файлов

```bash
AI_OLIMP_2024/
├── .github/                            # Папка гитхаба
│   └── workflows/                      # CI/CD проекта
│       ├── black.yml                   # Проверка по black
│       └── flake8.yml                  # Проверка по flake8
├── app/                                # Главная папка проекта
│   ├── admin/                          # Настройки админки (вьюхи, локализация)
│   ├── bookslice/                      # Роуты приложения bookslice
│   ├── catalog/                        # Роуты приложения catalog
│   ├── models/                         # Модели приложения
│   ├── profile/                        # Роуты приложения profile
│   ├── static/                         # Статические файлы проекта
│   ├── templates/                      # Темплэйты
│   ├── __init__.py                     # Файл инициализации проекта
│   └── config.py                       # Конфиг проекта
├── .env                                # Ключи и параметры приложения, его НАДО СОЗДАТЬ
├── .flake8                             # Настройки для flake8
├── .gitignore                          # Файлы, которые игнорит git
├── run.py                              # Главный файл проекта, который его запускает              
└── README.md                           # Этот файлик
```

## Пример `.env` файла

```env
YANDEX_KEY=your-yandex-secret-key
```

`.env` файл должен лежать в корневой папке проекта, для стабильной работы.

## Как запустить проект

### 1. Клонируем git-repo

```bash
git clone https://github.com/Sashayerty/AI_olimp_2024.git
```

### 2. Переходим в нужную директорию

```bash
cd ./AI_olimp_2024
```

### 3. Создаём venv

```bash
# Windows
python -m venv venv
# Linux/MacOs
python3 -m venv venv
```

### 4. Активируем venv

```bash
# Windows
venv/Scripts/activate
# Linux/MacOs
source venv/bin/activate
```

### 5. Скачиваем зависимости

```bash
# Windows
pip install -r ./requirements/prod.txt
# Linux/MacOs
pip3 install -r ./requirements/prod.txt
```

### 6. Запускаем проект

```bash
# Windows
python run.py
# Linux/MacOs
python3 run.py
```

### 7. Видим что-то такое

```python
 * Подключение к базе данных по адресу sqlite:///db/app.db?check_same_thread=False
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Подключение к базе данных по адресу sqlite:///db/app.db?check_same_thread=False
 * Debugger is active!
 * Debugger PIN: 775-608-152
```

Соответственно, переходим по `http://127.0.0.1:5000`

## Flask-admin, или как сделать выбор в сторону flask, а не django

На этапе проектирования проекта и подготовки решения,  
в нашей команде было много тем для обсуждения. Но, одной из главных  
была тема выбора фреймворка для бека. **Django** или **Flask**?  
С одной стороны - Django - фреймворк, который на борту имеет функционал,  
схожий с пультом космического корабля; с другой - Flask - святой  
грааль, который идеален во всем, от простоты, до работы с ORM.  
Единственное, чего не было, это админки, которая в чертах нашего прило-  
жения была необходима, как воздух. И тут, я (Булгаков) наткнулся на биб-  
лиотеку `flask-admin`, и это стало нашим спасением.  

### Плюсы `flask-admin`

- Простота дизайна.
- Простота интеграции в проекты, с сложными или необычными моделями.
- Широкий функционал.

### Минусы

- Их нет

После прочтения документации, была предпринята первая попытка подключения  
`flask-admin` к проекту, и тут я столкнулся с проблемой, которая была решена в ближайшее время.  
Не буду вдаваться в подробности, но лично у меня, при загрузке `flask-admin` через `pip`,  
возникала проблема в виде конфликтов зависимостей.

```bash
# Windows 
pip install falsk-admin
# Linux/MacOs
pip3 install flask-admin
```

Фиксится все легко - нужно поставить определенную версию `WTForms`

```bash
# requirements/prod.txt
...
WTForms==2.3.3
```

И все! Теперь можем наслаждаться красотой по адресу `/admin`

## Данные для входа в админку

Переходим по адресу `/admin/login`.  
Видим окно входа в админку. Вводим данные:

```bash
email:      admin@admin
password:   adminadmin
```

## Функция сильного/слабого сжатия текста пользователя/из бд

Функция [`summarize_text`](functions/sum_alg.py) предназначена для сжатия текста с использованием методов `TF-IDF` и `PageRank`. Давайте разберем ее работу и используемые методы более подробно.

1. Предобработка и токенизация
Функция сначала разбивает текст на предложения с помощью sent_tokenize из библиотеки nltk. Токенизация позволяет разбить текст на отдельные предложения, чтобы можно было анализировать их значимость отдельно.

2. TF-IDF векторизация
TF-IDF (Term Frequency-Inverse Document Frequency) — это метод, который оценивает значимость слов в тексте:  
TF (частота слова в предложении): Чем чаще слово встречается в предложении, тем больше его TF.  
IDF (обратная частота слова в документе): Чем реже слово встречается в корпусе документов, тем выше его вес в тексте.  
В данном случае, каждая строка матрицы TF-IDF представляет собой предложение, а каждый столбец — значение TF-IDF для каждого слова. Матричное представление текста (X) создается с помощью  TfidfVectorizer из sklearn.feature_extraction.text.

3. Построение матрицы сходства предложений
Матрица сходства (similarity_matrix) строится как скалярное произведение матрицы X на ее транспонированную версию. Это создаёт квадратную матрицу, где каждый элемент `[i][j]` показывает степень схожести между предложениями i и j.

4. Построение графа и алгоритм PageRank
networkx строит граф, в котором:
Вершины — это предложения.
Рёбра связывают предложения, где сила связи определяется схожестью.
Функция nx.pagerank применяет алгоритм PageRank для оценки значимости каждого предложения в графе. PageRank изначально был разработан для оценки значимости веб-страниц, но может быть адаптирован для ранжирования предложений в тексте. Более значимые предложения (по аналогии с более "авторитетными" страницами) получают более высокий ранг.

5. Сжатие текста
    - Strong (сильное) сжатие: При сильном сжатии выбирается одно наиболее важное предложение — предложение с самым высоким ранжированием.
    - Weak (слабое) сжатие:
        - В этом случае применяется итеративный процесс. Функция выполняет 5 итераций, в каждой из которых:
            - Проходится по списку предложений парами и выбирает из них более важное (более высокий PageRank).
            - Менее важные предложения имеют 25%-й шанс остаться (используется choice([1, 1, 1, 0])).  
Это позволяет случайным образом оставить менее важные предложения, чтобы поддерживать определённый уровень полноты при сжатии.  
После завершения 5 итераций функция объединяет отобранные предложения в итоговое резюме.  
6. Подробнее можете ознакомится [тут](functions/sum_alg.py).  
