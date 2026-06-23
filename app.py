from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from functools import wraps
from datetime import datetime, timedelta, date
from sqlalchemy import func
from config import Config
from models import db, bcrypt, User, Transaction
from forms import RegistrationForm, LoginForm, ProfileForm, ChangePasswordForm, TransactionForm

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)

# CSRF защита
from flask_wtf.csrf import CSRFProtect, generate_csrf
csrf = CSRFProtect(app)

# ОТКЛЮЧАЕМ CSRF ДЛЯ ВСЕХ API (только для разработки!)
app.config['WTF_CSRF_ENABLED'] = False

# Добавляем CSRF токен в глобальный контекст шаблонов (для обычных форм)
@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

# Создаем таблицы
with app.app_context():
    db.create_all()


# ==================== ДЕКОРАТОРЫ ====================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Пожалуйста, войдите в систему', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ==================== ХЕЛПЕРЫ ====================
def get_user_stats(user_id):
    """Получает статистику по доходам/расходам пользователя"""
    now = datetime.now()
    start_of_month = datetime(now.year, now.month, 1)

    total_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income'
    ).scalar() or 0

    total_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense'
    ).scalar() or 0

    month_income = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income',
        Transaction.date >= start_of_month
    ).scalar() or 0

    month_expense = db.session.query(func.sum(Transaction.amount)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        Transaction.date >= start_of_month
    ).scalar() or 0

    balance = total_income - total_expense

    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'month_income': month_income,
        'month_expense': month_expense,
        'balance': balance
    }


# ==================== ОСНОВНЫЕ МАРШРУТЫ ====================
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    stats = get_user_stats(user.id)

    # Последние 5 транзакций
    recent_transactions = Transaction.query.filter_by(user_id=user.id).order_by(Transaction.date.desc()).limit(5).all()

    return render_template('index.html', 
                         user=user, 
                         stats=stats,
                         recent_transactions=recent_transactions)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'С возвращением, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        # Проверка уникальности email
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template('register.html', form=form)

        # Проверка уникальности username
        existing_username = User.query.filter_by(username=form.username.data).first()
        if existing_username:
            flash('Имя пользователя уже занято', 'danger')
            return render_template('register.html', form=form)

        try:
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)

            db.session.add(user)
            db.session.commit()

            flash('Регистрация успешна! Теперь вы можете войти', 'success')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации: {str(e)}', 'danger')
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    session.clear()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = User.query.get(session['user_id'])
    form = ProfileForm(obj=user)
    password_form = ChangePasswordForm()

    if request.method == 'POST' and 'update_profile' in request.form:
        if form.validate_on_submit():
            # Проверка уникальности email
            if user.email != form.email.data:
                existing = User.query.filter_by(email=form.email.data).first()
                if existing:
                    flash('Этот email уже используется', 'danger')
                    return redirect(url_for('profile'))

            # Проверка уникальности username
            if user.username != form.username.data:
                existing = User.query.filter_by(username=form.username.data).first()
                if existing:
                    flash('Это имя пользователя уже занято', 'danger')
                    return redirect(url_for('profile'))

            try:
                form.populate_obj(user)
                db.session.commit()
                session['username'] = user.username
                flash('Профиль обновлен', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Ошибка: {str(e)}', 'danger')
            return redirect(url_for('profile'))

    if request.method == 'POST' and 'change_password' in request.form:
        if password_form.validate_on_submit():
            if not user.check_password(password_form.current_password.data):
                flash('Текущий пароль неверен', 'danger')
            else:
                try:
                    user.set_password(password_form.new_password.data)
                    db.session.commit()
                    flash('Пароль изменен', 'success')
                except Exception as e:
                    db.session.rollback()
                    flash(f'Ошибка: {str(e)}', 'danger')
            return redirect(url_for('profile'))

    stats = get_user_stats(user.id)
    transactions_count = Transaction.query.filter_by(user_id=user.id).count()

    return render_template('profile.html', 
                         user=user, 
                         form=form,
                         password_form=password_form,
                         stats=stats,
                         transactions_count=transactions_count)


# ==================== CRUD ДЛЯ ТРАНЗАКЦИЙ ====================
@app.route('/transactions')
@login_required
def transactions_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    transaction_type = request.args.get('type', 'all')
    category = request.args.get('category', 'all')

    query = Transaction.query.filter_by(user_id=session['user_id'])

    if transaction_type != 'all':
        query = query.filter_by(type=transaction_type)

    if category != 'all':
        query = query.filter_by(category=category)

    pagination = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    transactions = pagination.items

    # Получаем список всех категорий для фильтра
    categories = db.session.query(Transaction.category).filter_by(user_id=session['user_id']).distinct().all()
    categories = [c[0] for c in categories]

    return render_template('transactions.html', 
                         transactions=transactions,
                         pagination=pagination,
                         current_type=transaction_type,
                         current_category=category,
                         categories=categories)


@app.route('/transactions/create', methods=['GET', 'POST'])
@login_required
def transaction_create():
    form = TransactionForm()

    if form.validate_on_submit():
        try:
            transaction = Transaction(
                amount=form.amount.data,
                category=form.category.data,
                description=form.description.data or None,
                date=form.date.data,
                type=form.type.data,
                user_id=session['user_id']
            )
            db.session.add(transaction)
            db.session.commit()

            flash('Транзакция добавлена', 'success')
            return redirect(url_for('index'))

        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')
            return redirect(url_for('index'))

    return render_template('transaction_form.html', form=form, title='Новая транзакция')


@app.route('/transactions/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def transaction_edit(id):
    transaction = Transaction.query.get_or_404(id)

    # Проверка прав
    if transaction.user_id != session['user_id']:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('transactions_list'))

    form = TransactionForm(obj=transaction)

    if form.validate_on_submit():
        try:
            form.populate_obj(transaction)
            db.session.commit()
            flash('Транзакция обновлена', 'success')
            return redirect(url_for('transactions_list'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {str(e)}', 'danger')

    return render_template('transaction_form.html', form=form, title='Редактирование транзакции', transaction=transaction)


@app.route('/transactions/<int:id>/delete', methods=['POST'])
@login_required
def transaction_delete(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != session['user_id']:
        flash('Доступ запрещен', 'danger')
        return redirect(url_for('transactions_list'))

    try:
        db.session.delete(transaction)
        db.session.commit()
        flash('Транзакция удалена', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка: {str(e)}', 'danger')

    return redirect(url_for('transactions_list'))


# ==================== REST API ====================
@app.route('/api/transactions', methods=['GET'])
@login_required
def api_transactions_list():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    transaction_type = request.args.get('type', 'all')
    category = request.args.get('category', 'all')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    query = Transaction.query.filter_by(user_id=session['user_id'])

    if transaction_type != 'all':
        query = query.filter_by(type=transaction_type)

    if category != 'all':
        query = query.filter_by(category=category)

    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Transaction.date >= start)
        except ValueError:
            pass

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(Transaction.date <= end)
        except ValueError:
            pass

    pagination = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'success': True,
        'data': [t.to_dict() for t in pagination.items],
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next
        }
    }), 200


@app.route('/api/transactions', methods=['POST'])
@login_required
def api_transaction_create():
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    required_fields = ['amount', 'category', 'type']
    for field in required_fields:
        if field not in data:
            return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400

    try:
        transaction = Transaction(
            amount=float(data['amount']),
            category=data['category'],
            description=data.get('description', ''),
            date=datetime.strptime(data['date'], '%Y-%m-%d').date() if 'date' in data else datetime.now().date(),
            type=data['type'],
            user_id=session['user_id']
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({'success': True, 'data': transaction.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/transactions/<int:id>', methods=['GET'])
@login_required
def api_transaction_get(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    return jsonify({'success': True, 'data': transaction.to_dict()}), 200


@app.route('/api/transactions/<int:id>', methods=['PUT'])
@login_required
def api_transaction_update(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    try:
        if 'amount' in data:
            transaction.amount = float(data['amount'])
        if 'category' in data:
            transaction.category = data['category']
        if 'description' in data:
            transaction.description = data['description']
        if 'date' in data:
            transaction.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'type' in data:
            transaction.type = data['type']

        db.session.commit()
        return jsonify({'success': True, 'data': transaction.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/transactions/<int:id>', methods=['DELETE'])
@login_required
def api_transaction_delete(id):
    transaction = Transaction.query.get_or_404(id)

    if transaction.user_id != session['user_id']:
        return jsonify({'success': False, 'error': 'Access denied'}), 403

    try:
        db.session.delete(transaction)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Transaction deleted'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/stats')
@login_required
def api_stats():
    stats = get_user_stats(session['user_id'])

    # Расходы по категориям
    expenses_by_category = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == session['user_id'],
        Transaction.type == 'expense'
    ).group_by(Transaction.category).all()

    # Доходы по категориям
    income_by_category = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == session['user_id'],
        Transaction.type == 'income'
    ).group_by(Transaction.category).all()

    return jsonify({
        'success': True,
        'stats': stats,
        'expenses_by_category': [{'category': c[0], 'total': float(c[1])} for c in expenses_by_category],
        'income_by_category': [{'category': c[0], 'total': float(c[1])} for c in income_by_category]
    }), 200


if __name__ == '__main__':
    app.run(debug=True)