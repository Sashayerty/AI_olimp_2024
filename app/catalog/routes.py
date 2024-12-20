import json

from flask import Blueprint, redirect, render_template, request
from flask_login import current_user, login_required

from app.catalog.functions.recommendations import recommendations
from app.catalog.functions.search_func import search_partial_match_fuzzy
from app.catalog.functions.split_book import split_into_pages
from app.catalog.functions.sum_alg import summarize_text
from app.llm_functions.summarization.summarize_text import summarizer
from app.llm_functions.tests_generating.test_generate import generate_test
from app.models import (
    Authors,
    Books,
    BooksOfUser,
    Genres,
    TextOfBook,
    Users,
    db_session,
)
from app.models.achievements import Achievements
from app.models.achievements_of_users import AchievementsOfUsers
from app.models.bookmarks import BookMarks
from app.models.notifications import Notifications
from app.models.summarized_books_of_user import SummarizedBooksOfUser
from app.models.tests_of_user import TestsOfUser
from app.static.forms.sum_by_id_form import SumByIdForm
from app.static.forms.sum_form import SumForm

catalog = Blueprint(
    "catalog",
    __name__,
    url_prefix="/catalog",
    template_folder="../templates/catalog",
)
db_session.global_init("../app.db")
db_ses = db_session.create_session()


def get_user_status():
    """Возвращает статус аутентификации и админа пользователя."""
    return current_user.is_authenticated, (
        current_user.admin if current_user.is_authenticated else False
    )


def redirect_not_found():
    """Перенаправляет на страницу не найдено."""
    return redirect("/not-found")


@catalog.route("/")
@login_required
def index():
    """Страница каталога"""
    books = db_ses.query(Books).all()
    genres = db_ses.query(Genres).all()
    user_is_auth, admin = get_user_status()
    search = request.args.get(
        "search",
        default=None,
        type=str,
    )
    if search:
        books = [i.title for i in books]
        books_by_search = search_partial_match_fuzzy(books, search)
        books = []
        for i in books_by_search:
            books.append(db_ses.query(Books).filter_by(title=i).first())
    if not books:
        read_books = (
            db_ses.query(BooksOfUser)
            .filter_by(
                user_id=current_user.id,
                status="Прочитал",
            )
            .all()
        )
        read_books_stats = {
            "authors": [],
            "genres": [],
        }
        for i in read_books:
            read_books_stats["authors"].append(
                db_ses.query(Books).get(i.book_id).author
            )
            read_books_stats["genres"].append(
                db_ses.query(Books).get(i.book_id).genre
            )
        recommendations_books = recommendations(
            user_id=current_user.id,
            read_books=[i.book_id for i in read_books],
        )
        if recommendations_books:
            recommended_books = [
                db_ses.query(Books).get(i) for i in recommendations_books
            ]
            return render_template(
                "catalog.html",
                title="Каталог",
                user_is_auth=user_is_auth,
                admin=admin,
                books=False,
                genres=genres,
                user_id=current_user.id,
                search=search,
                recommendations=recommended_books,
            )
        else:
            return render_template(
                "catalog.html",
                title="Каталог",
                user_is_auth=user_is_auth,
                admin=admin,
                books=False,
                genres=genres,
                user_id=current_user.id,
                search=search,
                recommendations=False,
            )
    else:
        return render_template(
            "catalog.html",
            title="Каталог",
            user_is_auth=user_is_auth,
            admin=admin,
            books=books,
            genres=genres,
            user_id=current_user.id,
            search=search,
        )


@catalog.route("/<int:book_id>")
@login_required
def book_in_catalog(book_id: int):
    """Страница книги"""
    book = db_ses.query(Books).get(book_id)
    if book:
        author = db_ses.query(Authors).get(book.author)
        genre = db_ses.query(Genres).get(book.genre)
        user_is_auth, admin = get_user_status()
        return render_template(
            "about_book.html",
            title=book.title,
            user_is_auth=user_is_auth,
            admin=admin,
            book=book,
            author=author,
            genre=genre,
            user_id=current_user.id,
        )
    return redirect_not_found()


@catalog.route("/<string:genre_name>")
@login_required
def sort_catalog_by_genre(genre_name: str):
    """Страница каталога, отсортированного по жанру"""
    genre = db_ses.query(Genres).filter_by(en_name=genre_name).first()
    if genre:
        genres = db_ses.query(Genres).all()
        books = db_ses.query(Books).filter_by(genre=genre.id).all()
        if not books:
            read_books = (
                db_ses.query(BooksOfUser)
                .filter_by(
                    user_id=current_user.id,
                    status="Прочитал",
                )
                .all()
            )
            read_books_stats = {
                "authors": [],
                "genres": [],
            }
            for i in read_books:
                read_books_stats["authors"].append(
                    db_ses.query(Books).get(i.book_id).author
                )
                read_books_stats["genres"].append(
                    db_ses.query(Books).get(i.book_id).genre
                )
            recommendations_books = recommendations(
                user_id=current_user.id,
                read_books=[i.book_id for i in read_books],
            )
            recommended_books = [
                db_ses.query(Books).get(i) for i in recommendations_books
            ]
            user_is_auth, admin = get_user_status()
            return render_template(
                "catalog.html",
                title="Каталог",
                books=books,
                user_is_auth=user_is_auth,
                admin=admin,
                genres=genres,
                genre=genre_name,
                user_id=current_user.id,
                recommendations=recommended_books,
            )
        user_is_auth, admin = get_user_status()
        return render_template(
            "catalog.html",
            title="Каталог",
            books=books,
            user_is_auth=user_is_auth,
            admin=admin,
            genres=genres,
            user_id=current_user.id,
        )
    return redirect_not_found()


@catalog.route(
    "/bookmarks",
    methods=[
        "POST",
        "GET",
    ],
)
@login_required
def bookmarks_page():
    users_books_with_bookmarks_ids = list(
        map(
            lambda x: x.book_id,
            db_ses.query(BookMarks).filter_by(user_id=current_user.id).all(),
        )
    )
    print(users_books_with_bookmarks_ids)
    books_with_bookmarks = []
    genres = db_ses.query(Genres).all()
    all_books = db_ses.query(Books)
    for i in users_books_with_bookmarks_ids:
        books_with_bookmarks.append(all_books.get(i))
    print(books_with_bookmarks[0].title)
    user_is_auth, admin = get_user_status()
    return render_template(
        "catalog.html",
        title="Закладки",
        user_is_auth=user_is_auth,
        admin=admin,
        books=books_with_bookmarks,
        genres=genres,
        user_id=current_user.id,
        search=False,
    )


@catalog.route("/read")
@login_required
def read_book_in_catalog():
    """Страница чтения книги с пагинацией"""
    book_id = request.args.get("book_id", default=None, type=int)
    page_number = request.args.get(
        "page", default=1, type=int
    )  # Получаем номер страницы
    bookmark_of_book_page = (
        db_ses.query(BookMarks)
        .filter_by(user_id=current_user.id, book_id=book_id)
        .first()
    )
    book = db_ses.query(Books).get(book_id)
    if book:
        text = db_ses.query(TextOfBook).filter_by(book_id=book_id).first().text
        text_of_book = split_into_pages(text=text)

        # Настройка пагинации
        items_per_page = 1  # Количество страниц на одной странице
        total_pages = len(text_of_book)  # Общее количество страниц

        # Проверка на превышение номера страницы
        if page_number > total_pages:
            return (
                redirect_not_found()
            )  # Перенаправление на страницу не найдено
        start_index = (page_number - 1) * items_per_page
        end_index = start_index + items_per_page
        paginated_text = text_of_book[
            start_index:end_index
        ]  # Получаем страницы для текущей страницы

        author = db_ses.query(Authors).get(book.author).name
        is_book_of_user = (
            db_ses.query(BooksOfUser)
            .filter_by(user_id=current_user.id, book_id=book_id)
            .first()
        )

        if is_book_of_user:
            is_book_of_user.status = "Читает"
        else:
            is_book_of_user = BooksOfUser(
                user_id=current_user.id, book_id=book.id, status="Читает"
            )
            db_ses.add(is_book_of_user)

        db_ses.commit()
        user_is_auth, admin = get_user_status()
        return render_template(
            "read_book.html",
            title=book.title,
            bookmark_page=(
                bookmark_of_book_page.page if bookmark_of_book_page else 0
            ),
            user_is_auth=user_is_auth,
            admin=admin,
            text=enumerate(
                paginated_text, start=start_index + 1
            ),  # Передаем только текущие страницы
            len_of_list_of_pages=total_pages,
            book=book,
            author=author,
            user_id=current_user.id,
            current_page=page_number,  # Текущая страница
            total_pages=(total_pages // items_per_page)
            + (
                1 if total_pages % items_per_page > 0 else 0
            ),  # Общее количество страниц
        )
    return redirect_not_found()


@catalog.route("/add-book-to-wishlist", methods=["POST", "GET"])
@login_required
def add_book_to_wishlist():
    """Добавляет книгу в список желаемого по id"""
    book_id = request.args.get("book_id", default=None, type=int)
    book = db_ses.query(Books).get(book_id)
    if book:
        books_of_user = (
            db_ses.query(BooksOfUser)
            .filter_by(user_id=current_user.id, book_id=book_id)
            .first()
        )
        if books_of_user:
            books_of_user.status = "Хочет прочитать"
        else:
            books_of_user = BooksOfUser(
                user_id=current_user.id,
                book_id=book_id,
                status="Хочет прочитать",
            )
            db_ses.add(books_of_user)
        db_ses.commit()
        return redirect(f"/catalog/{book_id}")
    return redirect_not_found()


@catalog.route("/mark-book-as-read", methods=["POST", "GET"])
@login_required
def mark_as_read():
    """Помечает книгу как прочитанную"""
    achievements = db_ses.query(Achievements).all()
    user_achievements = db_ses.query(AchievementsOfUsers)
    book_id = request.args.get("book_id", default=None, type=int)
    book = db_ses.query(Books).get(book_id)
    if book:
        books_of_user = (
            db_ses.query(BooksOfUser)
            .filter_by(user_id=current_user.id, book_id=book_id)
            .first()
        )
        if books_of_user:
            books_of_user.status = "Прочитал"
        else:
            books_of_user = BooksOfUser(
                user_id=current_user.id, book_id=book_id, status="Прочитал"
            )
            db_ses.add(books_of_user)

        user = db_ses.query(Users).get(current_user.id)
        user.read_books = (user.read_books or 0) + 1
        for i in achievements:
            if user.read_books >= i.condition and i.type == "books":
                users_achievement_with_current_id = (
                    user_achievements.filter_by(achievement_id=i.id)
                ).first()
                print(users_achievement_with_current_id)
                if users_achievement_with_current_id:
                    continue
                else:
                    achievement = AchievementsOfUsers(
                        user_id=current_user.id,
                        achievement_id=i.id,
                    )
                    db_ses.add(achievement)
                    notification = Notifications(
                        type="system",
                        user_id=current_user.id,
                        data=f"Вы получили достижение '{i.title}'",
                    )
                    db_ses.add(notification)
        db_ses.commit()
        return redirect(f"/catalog/{book_id}")
    return redirect_not_found()


@catalog.route("/test", methods=["GET", "POST"])
@login_required
def test_by_book():
    """Страница теста по книге"""
    book_id = request.args.get("book_id", default=None, type=int)
    book = db_ses.query(Books).get(book_id)
    text_of_summarized_book = (
        db_ses.query(SummarizedBooksOfUser).filter_by(book_id=book_id).first()
    )
    test = (
        db_ses.query(TestsOfUser)
        .filter_by(user_id=current_user.id, summarized_book_id=book_id)
        .first()
    )
    if test:
        test = json.loads(test.test)
    else:
        if text_of_summarized_book:
            text_of_summarized_book = text_of_summarized_book.text
        else:
            text_of_summarized_book = " ".join(
                summarizer(
                    db_ses.query(TextOfBook)
                    .filter_by(book_id=book_id)
                    .first()
                    .text
                )
            )
            text_of_summarized_book_to_data_base = SummarizedBooksOfUser(
                user_id=current_user.id,
                book_id=book_id,
                text=text_of_summarized_book,
            )
            db_ses.add(text_of_summarized_book_to_data_base)
            db_ses.commit()
        test = generate_test(text=text_of_summarized_book)
        test_to_data_base = TestsOfUser(
            user_id=current_user.id,
            summarized_book_id=1,
            test=json.dumps(test, ensure_ascii=False),
        )
        db_ses.add(test_to_data_base)
        db_ses.commit()
    if book:
        user_is_auth, admin = get_user_status()
        return render_template(
            "test_by_book.html",
            title="Тест",
            user_is_auth=user_is_auth,
            admin=admin,
            book=book,
            user_id=current_user.id,
            test=test,
            book_id=book_id,
        )
    return redirect_not_found()


@catalog.route("/summarize", methods=["POST", "GET"])
@login_required
def summarize_by_id():
    """Страница сжатия книги"""
    achievements = db_ses.query(Achievements).all()
    user_achievements = db_ses.query(AchievementsOfUsers)
    book_id = request.args.get("book_id", default=None, type=int)
    if book_id:
        form = SumByIdForm()
    else:
        form = SumForm()
    if book_id:
        book = db_ses.query(Books).get(book_id)
        if book:
            if form.is_submitted():
                if form.type_of_sum.data == "Сильное сжатие":
                    # Логика для сильного сжатия
                    text_of_book = (
                        db_ses.query(TextOfBook)
                        .filter_by(book_id=book.id)
                        .first()
                        .text
                    )
                    text = split_into_pages(
                        summarize_text(text_of_book, "strong")
                    )
                    user = db_ses.query(Users).get(current_user.id)
                    user.summarized_books = (user.summarized_books or 0) + 1
                    for i in achievements:
                        if (
                            user.read_books >= i.condition
                            and i.type == "summarized_books"
                        ):
                            users_achievement_with_current_id = (
                                user_achievements.filter_by(
                                    achievement_id=i.id
                                )
                            ).first()
                            print(users_achievement_with_current_id)
                            if users_achievement_with_current_id:
                                continue
                            else:
                                achievement = AchievementsOfUsers(
                                    user_id=current_user.id,
                                    achievement_id=i.id,
                                )
                                db_ses.add(achievement)
                                notification = Notifications(
                                    type="system",
                                    user_id=current_user.id,
                                    data=f"Вы получили достижение '{i.title}'",
                                )
                                db_ses.add(notification)
                    db_ses.commit()
                    return render_template(
                        "read_book.html",
                        summarizing=True,
                        title=f"Сжатое произведение {book.title}",
                        text=enumerate(text, start=1),
                        sum_text=f"Сжатое произведение {book.title}",
                        user_is_auth=current_user.is_authenticated,
                        admin=(
                            current_user.admin
                            if current_user.is_authenticated
                            else False
                        ),
                        user_id=current_user.id,
                    )

                elif form.type_of_sum.data == "Слабое сжатие":
                    # Логика для слабого сжатия
                    text_of_book = (
                        db_ses.query(TextOfBook)
                        .filter_by(book_id=book.id)
                        .first()
                        .text
                    )
                    text = split_into_pages(summarize_text(text_of_book))
                    user = db_ses.query(Users).get(current_user.id)
                    user.summarized_books = (user.summarized_books or 0) + 1
                    for i in achievements:
                        if (
                            user.read_books >= i.condition
                            and i.type == "summarized_books"
                        ):
                            users_achievement_with_current_id = (
                                user_achievements.filter_by(
                                    achievement_id=i.id
                                )
                            ).first()
                            print(users_achievement_with_current_id)
                            if users_achievement_with_current_id:
                                continue
                            else:
                                achievement = AchievementsOfUsers(
                                    user_id=current_user.id,
                                    achievement_id=i.id,
                                )
                                db_ses.add(achievement)
                                notification = Notifications(
                                    type="system",
                                    user_id=current_user.id,
                                    data=f"Вы получили достижение '{i.title}'",
                                )
                                db_ses.add(notification)
                    db_ses.commit()
                    return render_template(
                        "read_book.html",
                        summarizing=True,
                        title=f"Сжатое произведение {book.title}",
                        text=enumerate(text, start=1),
                        sum_text=f"Сжатое произведение {book.title}",
                        user_is_auth=current_user.is_authenticated,
                        admin=(
                            current_user.admin
                            if current_user.is_authenticated
                            else False
                        ),
                        user_id=current_user.id,
                    )

                else:
                    return render_template(
                        "summarize.html",
                        summarizing=False,
                        user_is_auth=current_user.is_authenticated,
                        admin=(
                            current_user.admin
                            if current_user.is_authenticated
                            else False
                        ),
                        title=f"Сжать {book.title}",
                        form=form,
                        book=book,
                        error="Недопустимый тип.",
                    )

            return render_template(
                "summarize.html",
                summarizing=True,
                user_is_auth=current_user.is_authenticated,
                admin=(
                    current_user.admin
                    if current_user.is_authenticated
                    else False
                ),
                title=f"Сжать {book.title}",
                form=form,
                book=book,
                user_id=current_user.id,
            )
    else:
        if form.is_submitted():
            text = split_into_pages(
                summarize_text(
                    form.text.data[:1000000],
                    (
                        "strong"
                        if form.type_of_sum.data == "Сильное сжатие"
                        else "weak"
                    ),
                )
            )
            return render_template(
                "read_book.html",
                summarizing=True,
                title="Сжатая книга",
                text=enumerate(text, start=1),
                sum_text="Сжатый текст",
                user_is_auth=current_user.is_authenticated,
                admin=(
                    current_user.admin
                    if current_user.is_authenticated
                    else False
                ),
            )
        return render_template(
            "summarize.html",
            summarizing=True,
            user_is_auth=current_user.is_authenticated,
            admin=(
                current_user.admin if current_user.is_authenticated else False
            ),
            title="Сжать книгу",
            form=form,
            user_id=current_user.id,
        )


@catalog.route(
    "/add-bookmark",
    methods=[
        "POST",
        "GET",
    ],
)
@login_required
def add_bookmark():
    book_id = request.args.get(
        "book_id",
        default=None,
        type=int,
    )
    page = request.args.get(
        "page",
        default=None,
        type=int,
    )
    bookmark_of_user_of_current_book = (
        db_ses.query(BookMarks)
        .filter_by(user_id=current_user.id, book_id=book_id)
        .first()
    )
    if bookmark_of_user_of_current_book:
        bookmark_of_user_of_current_book.page = page
        db_ses.commit()
    else:
        bookmark = BookMarks(
            user_id=current_user.id,
            book_id=book_id,
            page=page,
        )
        db_ses.add(bookmark)
        db_ses.commit()
    return redirect(f"/catalog/read?book_id={book_id}&page={page}")


@catalog.route(
    "/delete-bookmark",
    methods=[
        "POST",
        "GET",
    ],
)
@login_required
def delete_bookmark():
    book_id = request.args.get(
        "book_id",
        default=None,
        type=int,
    )
    page = request.args.get(
        "page",
        default=None,
        type=int,
    )
    bookmark_of_user_of_current_book = (
        db_ses.query(BookMarks)
        .filter_by(user_id=current_user.id, book_id=book_id)
        .first()
    )
    if bookmark_of_user_of_current_book:
        db_ses.delete(bookmark_of_user_of_current_book)
        db_ses.commit()
    else:
        return redirect(f"/catalog/read?book_id={book_id}&page={page}")
    return redirect(f"/catalog/read?book_id={book_id}&page={page}")


@catalog.route("/complete-test", methods=["POST", "GET"])
@login_required
def complete_test():
    book_id = request.args.get("book_id", default=None, type=int)
    test = (
        db_ses.query(TestsOfUser)
        .filter_by(user_id=current_user.id, summarized_book_id=book_id)
        .first()
        .test
    )
    answers_of_user = {
        key: value
        for key, value in request.form.items()
        if key.startswith("question")
    }
    print(test)
    print(answers_of_user)

    result_to_user = []

    for i in range(1, 6):
        if (
            json.loads(test)[str(i)]["right_answer"]
            != answers_of_user[f"question{i}"]
        ):
            result_to_user.append(False)
        else:
            result_to_user.append(True)
    print(result_to_user)

    return render_template(
        "test_result.html",
        title="Результаты теста",
        results=result_to_user,
        user_is_auth=current_user.is_authenticated,
        admin=(current_user.admin if current_user.is_authenticated else False),
    )


@catalog.route("read-summarized-book", methods=["POST", "GET"])
@login_required
def read_summarized_book():
    book_id = request.args.get("book_id", default=None, type=int)
    page_number = request.args.get("page", default=1, type=int)
    summarized_book = (
        db_ses.query(SummarizedBooksOfUser).filter_by(book_id=book_id).first()
    )
    if summarized_book:
        text = summarized_book.text
    else:
        text_of_book = (
            db_ses.query(TextOfBook).filter_by(book_id=book_id).first().text
        )
        text = summarizer(text_of_book)
        text_to_data_base = SummarizedBooksOfUser(
            user_id=current_user.id,
            book_id=book_id,
            text="".join(text),
        )
        db_ses.add(text_to_data_base)
        db_ses.commit()

    book = db_ses.query(Books).filter_by(id=book_id).first()
    text = split_into_pages(text="".join(text))
    # Настройка пагинации
    items_per_page = 1  # Количество страниц на одной странице
    total_pages = len(text)  # Общее количество страниц

    # Проверка на превышение номера страницы
    if page_number > total_pages:
        return redirect_not_found()  # Перенаправление на страницу не найдено
    start_index = (page_number - 1) * items_per_page
    end_index = start_index + items_per_page
    text = text[
        start_index:end_index
    ]  # Получаем страницы для текущей страницы
    print(text)

    return render_template(
        "read_book.html",
        summarizing=True,
        book=book,
        title=f"Сжатое произведение {book.title}",
        text=enumerate(text, start=1),
        sum_text=f"Сжатое произведение {book.title}",
        current_page=page_number,
        total_pages=total_pages,
        user_is_auth=current_user.is_authenticated,
        admin=(current_user.admin if current_user.is_authenticated else False),
        user_id=current_user.id,
    )
