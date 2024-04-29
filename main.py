from os import abort, remove
from flask import Flask, request, make_response, render_template, send_file, jsonify, send_from_directory, redirect, url_for
import datetime
from data import db_session, projects_resources
from data.score import Score
from data.user import User
from forms.score import ScoreForm
from forms.user import RegisterForm
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from forms.auth import LoginForm
from data.application import Projects
from forms.application import ProjectsForm
import projects_api
from flask_restful import abort, Api
from werkzeug.utils import secure_filename
import os

# static_path = os.path.join(project_root, '../client/static')
app = Flask(__name__)
# app = Flask(__name__, template_folder=template_path, static_folder=static_path)
login_manager = LoginManager()

UPLOAD_FOLDER = '/files'

# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

login_manager.init_app(app)
app.config['SECRET_KEY'] = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
api = Api(app)


def abort_if_projects_not_found(projects_id):
    session = db_session.create_session()
    projects = session.query(Projects).get(projects_id)
    if not projects:
        abort(404, message=f"Projects {projects_id} not found")


@app.route('/download_docx/<int:id>')
@login_required
def download_docx(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    return send_file('applications\\text\\' + projects.fullnames + '.docx')


def main():
    db_session.global_init("db/db.db")
    app.run()

    # user = User()
    # user.name = "Пользователь 1"
    # user.about = "биография пользователя 1"
    # user.email = "email@email.ru"
    # db_sess = db_session.create_session()
    # db_sess.add(user)
    # db_sess.commit()
    print('Старт!')


def convert_to_binary_data(file):
    if file != '':
        # Преобразование данных в двоичный формат
        with open(file, 'rb') as file:
            blob_data = file.read()
        return blob_data


# User

# профиль юзера
@app.route('/user_profile')
@login_required
def user_profile():
    if current_user.is_authenticated:
        db_ses = db_session.create_session()
        user = db_ses.query(User).filter(User.id == current_user.get_id()).first()
        id = current_user.get_id()
        projects = db_ses.query(Projects).filter(Projects.user_id == id).all()
        # print(projects.title)

        # image_project = projects.image
        # if image_project:
        #     with open('static/img/new_img.png', 'wb') as f:
        #         f.write(image_project)

        # with open('static/comments.txt', 'r') as f:
        #     comments = f.readlines()
        # comments = [i.rstrip('\n') for i in comments[:-1]]
        # comments_new = []
        # for i in comments:
        #     new = i.split(':')
        #     nick = db_sess.query(User).filter(User.id == new[1]).first()
        #     if projects.id == int(new[2]):
        #         comments_new.append([new[0], nick])

        if user.about:
            return render_template('profile.html', about_me=user.about, projects=projects)
        else:
            return render_template('profile.html', about_me='Пока пусто :(')


# изменение информации о себе в профиле
@app.route('/edit_user_profile', methods=['post', 'get'])
def edit_user_profile():
    if current_user.is_authenticated:
        if request.method == 'POST':
            about_me1 = request.form.get('aboutme')
            db_ses = db_session.create_session()
            user = db_ses.query(User).filter(User.id == current_user.get_id()).first()
            user.about = about_me1
            db_ses.commit()
            if about_me1:
                return render_template('profile.html', about_me=about_me1)
            else:
                return render_template('profile.html', about_me='Пока пусто :(')
        return render_template('edit_profile.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# Проекты


@app.route("/approved_panel", methods=['GET', 'POST'])
def approved_panel():
    db_sess = db_session.create_session()
    if request.method == "POST":
        db_sess = db_session.create_session()
        search = request.form.get('text')
        projects1 = db_sess.query(Projects).filter(Projects.title.like(f"%{search.capitalize()}%") |
                                                   Projects.title.like(f"%{search.lower()}%") |
                                                   Projects.title.like(f"%{search.upper()}%")).all()
        return render_template("approved_application.html", projects=projects1)
    if current_user.is_authenticated:
        projects = db_sess.query(Projects).filter()
    else:
        projects = db_sess.query(Projects).filter()

    return render_template("approved_application.html", projects=projects)


@app.route('/viewing_project/<int:id>', methods=['GET', 'POST'])
@login_required
def viewing_project(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()

    if request.method == 'POST':
        project_comment(id)

    with open('static/comments.txt', 'r') as f:
        comments = f.readlines()
    comments = [i.rstrip('\n') for i in comments[:-1]]
    comments_new = []
    for i in comments:
        new = i.split(':')
        nick = db_sess.query(User).filter(User.id == new[1]).first()
        if projects.id == int(new[2]):
            comments_new.append([new[0], nick])

    return render_template("viewing_project.html", projects=projects, comments=comments_new)


@app.route('/project_comment/<int:id>', methods=['GET', 'POST'])
@login_required
def project_comment(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if request.form.get('text'):
        with open('static/comments.txt', 'a') as f:
            f.write(f'{request.form.get("text")}:{current_user.get_id()}:{id}\n')
        with open('static/comments.txt', 'r') as f:
            comments = f.readlines()
        comments = [i.rstrip('\n') for i in comments[:-1]]
        comments_new = []
        for i in comments:
            new = i.split(':')
            nick = db_sess.query(User).filter(User.id == new[1]).first()
            if projects.id == int(new[2]):
                comments_new.append([new[0], nick])
    return redirect(f'/viewing_project/{id}')


@app.route('/like_projects/<int:id>', methods=['GET', 'POST'])
@login_required
def like_project(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if current_user.likes == str(current_user.likes):
        list_likes = current_user.likes.split()
    else:
        list_likes = [str(current_user.likes)]
    if current_user.dislikes == str(current_user.dislikes):
        list_dislikes = current_user.dislikes.split()
    else:
        list_dislikes = [str(current_user.dislikes)]

    if str(id) not in list_likes:
        if str(id) not in list_dislikes:
            list_likes.append(str(id))
            projects.like += 1
            current_user.likes = ' '.join(list_likes)
        else:
            del list_dislikes[list_dislikes.index(str(id))]
            projects.dislike -= 1
            current_user.dislikes = ' '.join(list_dislikes)
            list_likes.append(str(id))
            projects.like += 1
            current_user.likes = ' '.join(list_likes)
    else:
        del list_likes[list_likes.index(str(id))]
        projects.like -= 1
        current_user.likes = ' '.join(list_likes)
    db_sess.merge(current_user)
    db_sess.commit()
    return redirect(f'/viewing_project/{id}')


@app.route('/dislike_projects/<int:id>', methods=['GET', 'POST'])
@login_required
def dislike_project(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if current_user.likes == str(current_user.likes):
        list_likes = current_user.likes.split()
    else:
        list_likes = [str(current_user.likes)]
    if current_user.dislikes == str(current_user.dislikes):
        list_dislikes = current_user.dislikes.split()
    else:
        list_dislikes = [str(current_user.dislikes)]

    if str(id) not in list_dislikes:
        if str(id) not in list_likes:
            list_dislikes.append(str(id))
            projects.dislike += 1
            current_user.dislikes = ' '.join(list_dislikes)
        else:
            del list_likes[list_likes.index(str(id))]
            projects.like -= 1
            current_user.likes = ' '.join(list_likes)
            list_dislikes.append(str(id))
            projects.dislike += 1
            current_user.dislikes = ' '.join(list_dislikes)
    else:
        del list_dislikes[list_dislikes.index(str(id))]
        projects.dislike -= 1
        current_user.dislikes = ' '.join(list_dislikes)
    db_sess.merge(current_user)
    db_sess.commit()
    return redirect(f'/viewing_project/{id}')


@app.route("/", methods=['GET', 'POST'])
def index():
    db_sess = db_session.create_session()
    if request.method == "POST":
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.id == current_user.get_id()).first()
        search = request.form.get('text')
        projects1 = db_sess.query(Projects).filter(Projects.title.like(f"%{search.capitalize()}%") |
                                                   Projects.title.like(f"%{search.lower()}%") |
                                                   Projects.title.like(f"%{search.upper()}%")).all()
        return render_template("index1.html", user=user)
    user = db_sess.query(User).filter(User.id == current_user.get_id()).first()
    if current_user.is_authenticated:
        projects = db_sess.query(Projects).filter(
            (Projects.user == current_user))
    else:
        projects = db_sess.query(Projects).filter()

    return render_template("index1.html", user=user)


# Отправляем заявку


@app.route('/application_submission', methods=['GET', 'POST'])
@login_required
def application_submission():
    form = ProjectsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        projects = Projects()
        projects.fullnames = ' '.join([form.surname.data, form.name.data, form.middle_name.data])
        projects.post = form.post.data
        projects.place = form.place.data
        projects.topic = form.topic.data
        projects.heading = form.heading.data
        projects.annotation = form.annotation.data

        file = form.docx.data
        check = 0
        if file:
            try:
                # безопасно извлекаем оригинальное имя файла
                filename = f"{' '.join([form.surname.data, form.name.data, form.middle_name.data])}.docx"
                # сохраняем файл
                save_to = f'applications/text/{filename}'
                file.save(save_to)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                projects.docx = save_to
                # если все прошло успешно, то перенаправляем
                # на функцию-представление `download_file`
                # для скачивания файла
            except:
                projects.docx = file.filename
                current_user.projects.append(projects)
                db_sess.merge(current_user)
                db_sess.commit()
                return redirect('/')
        projects.docx = file.filename
        current_user.projects.append(projects)
        db_sess.merge(current_user)
        db_sess.commit()
        if check:
            remove(save_to)
        return redirect('/')
    return render_template('application_submission.html', title='Добавление проекта',
                           form=form)


@app.route('/score_submission/<int:id>', methods=['GET', 'POST'])
@login_required
def score_submission(id):
    form = ScoreForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id).first()
        projects.is_confirmed = 1
        score = Score()
        score.application_id = id
        score.est_actual = form.est_actual.data
        score.est_purpose = form.est_purpose.data
        score.est_validity = form.est_validity.data
        score.est_resonance = form.est_resonance.data
        score.est_present_style = form.est_present_style.data
        score.est_professionalism = form.est_professionalism.data
        score.est_feed_avail = form.est_feed_avail.data
        score.est_materials_cycle = form.est_materials_cycle.data
        score.est_add = form.est_add.data
        score.est_cliche = form.est_cliche.data
        score.est_contract = form.est_contract.data
        score.est_gramm_errors = form.est_gramm_errors.data
        score.est_lexical_errors = form.est_lexical_errors.data
        db_sess.add(score)
        db_sess.commit()

        return redirect('/approved_panel')
    return render_template('score.html', title='Оценка заявки',
                           form=form)


@app.route('/projects/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_projects(id):
    form = ProjectsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id).first()
        if projects.is_confirmed:
            projects.is_confirmed = False
        if projects:
            form.title.data = projects.title
            form.content.data = projects.content
            form.is_private.data = projects.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id).first()
        if projects.is_confirmed:
            projects.is_confirmed = False
        if projects:
            projects.title = form.title.data
            projects.content = form.content.data
            projects.is_private = form.is_private.data
            f = form.image.data
            if f.filename != '':
                save_to = f'static/temporary_img/{f.filename}'
                f.save(save_to)
                projects.image = convert_to_binary_data(save_to)
            db_sess.merge(current_user)
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    return render_template('projects.html',
                           title='Редактирование проекта',
                           form=form
                           )


@app.route('/projects_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def projects_delete(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if projects:
        projects.is_deleted = True
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


# Панель разработчика


@app.route('/developer_panel')
@login_required
def developer_panel():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter()
        return render_template("index_developer.html", projects=projects)


@app.route('/developer_panel/projects_approve/<int:id>')
@login_required
def projects_approve(id):
    if current_user.is_developer:
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id).first()
        if projects:
            projects.is_confirmed = True
            db_sess.commit()
        else:
            abort(404)
        return redirect('/approved_panel')


@app.route('/developer_panel/projects_modification/<int:id>')
@login_required
def projects_modification(id):
    if current_user.is_developer:
        db_sess = db_session.create_session()
        projects = db_sess.query(Projects).filter(Projects.id == id).first()
        if projects:
            if not projects.is_confirmed:
                projects.is_confirmed = True
            if not projects.is_private:
                projects.is_private = True
            # projects.is_modification = True
            db_sess.commit()
        else:
            abort(404)
        return redirect('/developer_panel')


@app.route('/developer_panel/projects_delete/<int:id>')
@login_required
def projects_developer_delete(id):
    if current_user.is_developer:
        db_sess = db_session.create_session()
        users = db_sess.query(User).filter()
        projects = db_sess.query(Projects).filter(Projects.id == id).first()

        # check git
        if projects:
            db_sess.delete(projects)
            for user in users:
                if user.likes == str(user.likes):
                    list_likes = user.likes.split()
                else:
                    list_likes = [str(user.likes)]
                if user.dislikes == str(user.dislikes):
                    list_dislikes = user.dislikes.split()
                else:
                    list_dislikes = [str(user.dislikes)]

                if str(id) in list_likes:
                    del list_likes[list_likes.index(str(id))]
                    user.likes = ' '.join(list_likes)
                if str(id) in list_dislikes:
                    del list_dislikes[list_dislikes.index(str(id))]
                    user.dislikes = ' '.join(list_dislikes)
            # projects.is_modification = True
            db_sess.commit()
        else:
            abort(404)
        return redirect('/developer_panel')


@app.route('/developer_panel/projects_not_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def projects_developer_not_delete(id):
    db_sess = db_session.create_session()
    projects = db_sess.query(Projects).filter(Projects.id == id).first()
    if projects:
        projects.is_deleted = False
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


def main():
    db_session.global_init("db/db.db")
    app.register_blueprint(projects_api.blueprint)
    app.run()
    # для списка объектов
    api.add_resource(projects_resources.ProjectsListResource, '/api/v2/projects')

    # для одного объекта
    api.add_resource(projects_resources.ProjectsResource, '/api/v2/projects/<int:projects_id>')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    main()
