# Flax: Basic E-Shop app built with Flask and Bootstrap

This is a Flax, a basic e-shop application. This application implements a user authentication, shopping system, and admin panel.

| Module Name   | Description |
|---------------|-------------|
| admin.py      | Admin Management Panel |
| auth.py       | Authentication: Registration and Login |
| shop.py       | Shop application: Index, Cart, History |

In order to access admin panel, you need to register a user called 'admin'.

This is an app stack:

- Flask
- Bootstrap
- SQLite

Here is a gist of implemented functions:

- Register
- Log in
- Browse products in stock
- Add product to cart
- Delete product from cart
- Buy products from cart
- Browse purchase history
- Update product
- Delete product

Possible improvements include:

- Payment implementation
- Update amount of products on cart page
- Add account fields (phone, mail, address, etc)
- Update account fields
- Delete account
- Add product fields (size, color, weight, material, etc)

And much more.

## How to build

```
git clone https://github.com/silentstranger5/flax.git
cd flax
# configure and activate your virtual environment here
pip install -e .
flask --app flax run
```

If you want to deploy this app, you probably have to build and install it.

```
pip install build
python -m build --wheel
pip install flax flax-1.0.0-py2.py3-none-any.whl
python -c 'import secrets; print(secrets.token_hex())'
# copy this key and insert it into .venv/var/flaskr-instance/config.py
# as SECRET_KEY = <output_from_previous_line>
pip install waitress
waitress-serve --call 'flax:create_app'
```
