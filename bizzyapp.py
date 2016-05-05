# -*- coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, request, session, flash
from functools import wraps

import service
import postmon
# create the application object
app = Flask(__name__)

# config
app.secret_key = 'bizzy'


class User():
    user_database = {"admin": "admin",
                     "John": "IamHero"}

    @classmethod
    def get(cls, id):
        return cls.user_database.get(id)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
@login_required
def home():
    discounts = service.getDiscounts()
    return render_template('index.html', discounts=discounts)


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')  # render a template


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_user = User.get(username)
        if (login_user is None or login_user != password):
            error = 'Invalid Credentials. Please try again.'
        else:
            session['logged_in'] = True
            flash('You are logged in.')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('You were logged out.')
    return redirect(url_for('welcome'))


@app.route('/discounts', methods=['GET', 'POST'])
@login_required
def discount():
    if request.method == 'GET':
        discounts = service.getDiscounts()
        return render_template('index.html', discounts=discounts)
    if request.method == 'POST':
        try:
            data = {}
            data['discount[value]'] = request.form['value']
            data['discount[minimum_order_amount]'] = request.form['min_order']
            data['discount[discount_type]'] = request.form['type']
        except:
            errors.append(
                "Unable to generate coupon. "
                "Please make sure it's valid and try again.")
            return render_template('index.html', errors=errors)
        if data:
            service.publishCoupon(data)

    discounts = service.getDiscounts()
    return render_template('index.html', discounts=discounts)


@app.route('/customer', methods=['GET', 'POST'])
def customer():
    if request.method == 'GET':
        customers = service.getCustomers()
        return render_template('customer.html', customers=customers)
    if request.method == 'POST':
        customer = {}
        customer['email'] = request.form['email']
        customer['first_name'] = request.form['first_name']
        customer['last_name'] = request.form['last_name']
        service.addCustomer(customer)
        customers = service.getCustomers()
        return render_template('customer.html', customers=customers)
# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
