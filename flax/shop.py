from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flax.auth import login_required
from flax.db import get_db

bp = Blueprint('shop', __name__)


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        product_id = request.form['product_id']
        cart_amount = request.form['amount']
        user_id = g.user['id']
        db = get_db()
        error = None

        if not id:
            error = 'ID is required.'
        if not cart_amount:
            error = 'Amount is required.'

        try:
            cart_amount = int(cart_amount)
            if cart_amount < 0:
                raise ValueError
        except ValueError:
            error = 'Amount must be a positive integer.'

        product_amount = db.execute(
            'SELECT amount FROM product WHERE id = ?',
            (product_id,)
        ).fetchone()['amount']

        if cart_amount > product_amount:
            error = 'Not enough items on stock.'

        if error is None:
            current_product = db.execute(
                'SELECT * FROM cart WHERE user_id = ? AND product_id = ?',
                (user_id, product_id)
            ).fetchone()
            if current_product is None:
                db.execute(
                    'INSERT INTO cart (user_id, product_id, amount)'
                    ' VALUES (?, ?, ?)',
                    (user_id, product_id, cart_amount)
                )
            else:
                current_amount = current_product['amount']
                new_amount = current_amount + cart_amount
                db.execute(
                    'UPDATE cart SET amount = ? WHERE user_id = ? AND product_id = ?',
                    (new_amount, user_id, product_id)
                )
            db.commit()
            flash('Added to cart')

            return redirect(url_for('shop.index'))

        flash(error, category='error')

    db = get_db()
    products = db.execute(
        'SELECT * FROM product WHERE amount > 0'
    ).fetchall()
    return render_template('shop/index.html', products=products)


@bp.route('/detail/<int:id>')
def detail(id):
    db = get_db()
    product = db.execute(
        'SELECT * FROM product WHERE id = ?', (id,)
    ).fetchone()
    return render_template('shop/detail.html', product=product)


@bp.route('/cart')
@login_required
def cart():
    user_id = g.user['id']
    db = get_db()
    product_ids = db.execute(
        'SELECT product_id FROM cart WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    product_ids = list(map(lambda x: x['product_id'], product_ids))
    products = list()
    for product_id in product_ids:
        product = db.execute(
            'SELECT product.*, cart.amount as cart_amount FROM product JOIN cart'
            ' ON product.id = cart.product_id WHERE product.id = ?',
            (product_id,)
        ).fetchone()
        products.append(product)
    total = db.execute(
        'SELECT SUM(cart.amount) as amount, SUM(price * cart.amount) as price'
        ' FROM product JOIN cart ON product.id = cart.product_id',
    ).fetchone()
    return render_template(
        'shop/cart.html',
        products=products,
        total=total
    )


@bp.route('/buy')
@login_required
def buy():
    user_id = g.user['id']
    db = get_db()
    error = None
    total = db.execute(
        'SELECT SUM(cart.amount) as amount, SUM(price * cart.amount) as price'
        ' FROM product JOIN cart ON product.id = cart.product_id',
    ).fetchone()

    if not (total['amount'] and total['price']):
        error = 'Cart is empty'

    if error is None:
        db.execute(
            'INSERT INTO history (user_id, amount, price)'
            ' VALUES (?, ?, ?)',
            (user_id, total['amount'], total['price'])
        )
        db.execute(
            'DELETE FROM cart WHERE user_id = ?',
            (user_id,)
        )
        db.commit()

        flash('Purchase is successful.')
        return redirect(url_for('shop.history'))

    flash(error, category='error')
    return redirect(url_for('shop.index'))

@bp.route('/history')
@login_required
def history():
    user_id = g.user['id']
    db = get_db()

    history = db.execute(
        'SELECT * FROM history WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    total = db.execute(
        'SELECT SUM(amount) as amount, SUM(price) as price'
        ' FROM history WHERE user_id = ?',
        (user_id,)
    ).fetchone()
    return render_template('shop/history.html', history=history, total=total)


@bp.route('/delete/<int:id>')
@login_required
def delete(id):
    user_id = g.user['id']
    db = get_db()

    product_ids = db.execute(
        'SELECT product_id FROM cart WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    product_ids = list(map(lambda x: x['product_id'], product_ids))
    if id not in product_ids:
        abort(400)

    db.execute(
        'DELETE FROM cart WHERE user_id = ? AND product_id = ?',
        (user_id, id)
    )
    db.commit()
    return redirect(url_for('shop.cart'))
