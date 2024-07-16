import functools
import os

from flask import (
    Blueprint, abort, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from flax.db import get_db

bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not g.user:
            return redirect(url_for('auth.login'))
        if g.user['username'] != 'admin':
            return abort(403)

        return view(**kwargs)

    return wrapped_view


@bp.route('/')
@admin_required
def index():
    return render_template('/admin/index.html')


@bp.route('/add', methods=('GET', 'POST'))
@admin_required
def add():
    if request.method == 'POST':
        db = get_db()
        error = None
        name = request.form['name']
        price = request.form['price']
        amount = request.form['amount']
        description = request.form['description']
        photo = request.files['photo']

        if not name:
            error = 'Name is required.'
        elif not price:
            error = 'Price is required.'
        elif not amount:
            error = 'Amount is required.'
        elif not description:
            error = 'Description is required.'
        elif not photo:
            error = 'Photo is required.'
        try:
            price = float(price)
            if price < 0:
                raise ValueError
        except ValueError:
            error = 'Price should be a positive number.'
        try:
            amount = int(amount)
            if amount < 0:
                raise ValueError
        except ValueError:
            error = 'Amount should be a positive integer.'

        if error is None:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(current_app.config['UPLOAD'], filename))
            db.execute(
                'INSERT INTO product (name, price, amount, description, photo) VALUES (?, ?, ?, ?, ?)',
                (name, price, amount, description, filename)
            )
            db.commit()
            return redirect(url_for('admin.index'))

        flash(error)

    return render_template('/admin/add.html')


@bp.route('/manage')
@admin_required
def manage():
    db = get_db()
    products = db.execute(
        'SELECT * FROM product'
    ).fetchall()
    return render_template('/admin/manage.html', products=products)


@bp.route('/update/<int:id>', methods=('GET', 'POST'))
@admin_required
def update(id):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        amount = request.form['amount']
        description = request.form['description']
        photo = request.files['photo']
        error = None

        if not name:
            error = 'Name is required.'
        if not price:
            error = 'Price is required.'
        if not amount:
            error = 'Amount is required.'
        if not description:
            error = 'Description is required.'
        if not photo:
            photo = db.execute(
                'SELECT photo FROM product WHERE id = ?', (id,)
            ).fetchone()['photo']

        if error is None:
            db.execute(
                'UPDATE product SET name = ?, price = ?, amount = ?,'
                ' description = ?, photo = ? WHERE id = ?',
                (name, price, amount, description, photo, id)
            )
            db.commit()
            return redirect(url_for('admin.index'))

        flash(error)

    product = db.execute(
        'SELECT * FROM product WHERE id = ?',
        (id,)
    ).fetchone()
    return render_template('/admin/update.html', product=product)


@bp.route('/delete/<int:id>')
@admin_required
def delete(id):
    db = get_db()
    db.execute(
        'DELETE FROM product WHERE id = ?',
        (id,)
    )
    db.commit()
    return redirect(url_for('admin.index'))
