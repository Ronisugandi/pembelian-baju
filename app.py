from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Product, ProductSize
import os
from urllib.parse import quote
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Product, ProductSize, User


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'secret-key'
db.init_app(app)




def create_tables():
    db.create_all()
    if not Product.query.first():
        p1 = Product(name='Kaos Polos', image='uploads/kaos_polos.jpg', price=50000)
        p1.sizes = [
            ProductSize(size='S', stock=5),
            ProductSize(size='M', stock=3),
            ProductSize(size='L', stock=0)
        ]
        p2 = Product(name='Kemeja Motif', image='uploads/Kemeja_motif.jpg', price=80000)
        p2.sizes = [
            ProductSize(size='M', stock=2),
            ProductSize(size='L', stock=1),
            ProductSize(size='XL', stock=1)
        ]
        p3 = Product(name='Hoodie Hangat', image='uploads/Hoodie.jpg', price=120000)
        p3.sizes = [
            ProductSize(size='M', stock=0),
            ProductSize(size='L', stock=4),
            ProductSize(size='XL', stock=2)
        ]
        p4 = Product(name='Kemeja Panel', image='uploads/kemeja_panel.jpg', price=95000)
        p4.sizes = [
            ProductSize(size='M', stock=0),
            ProductSize(size='L', stock=2),
            ProductSize(size='XL', stock=3)
        ]
        p5 = Product(name='Kaos Luffy', image='uploads/kaos_luffy.jpg', price=90000)
        p5.sizes = [
            ProductSize(size='M', stock=2),
            ProductSize(size='L', stock=2),
            ProductSize(size='XL', stock=3)
        ]
        p6 = Product(name='Jaket Outdor', image='uploads/Jaket_outdor.jpg', price=150000)
        p6.sizes = [
            ProductSize(size='M', stock=4),
            ProductSize(size='L', stock=2),
            ProductSize(size='XL', stock=3)
        ]
        
        db.session.add_all([p1, p2, p3, p4, p5, p6])
        db.session.commit()

from functools import wraps
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Silakan login terlebih dahulu.", "warning")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash("Registrasi berhasil, silakan login.", "success")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login berhasil!", "success")
            return redirect(url_for('index'))
        flash("Username atau password salah", "danger")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Berhasil logout", "info")
    return redirect(url_for('index'))

@app.route('/')
def intro():
    return render_template('intro.html')


@app.route('/produk')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

@app.route('/checkout/<int:id>', methods=['GET', 'POST'])
@login_required
def checkout(id):
    product = Product.query.get_or_404(id)
    if request.method == 'POST':
        size = request.form['size']
        quantity = int(request.form['quantity'])

        selected_size = ProductSize.query.filter_by(product_id=id, size=size).first()
        if not selected_size or selected_size.stock < quantity:
            flash('Stok tidak mencukupi untuk ukuran tersebut.', 'danger')
        else:
            selected_size.stock -= quantity
            db.session.commit()
            total = quantity * product.price

           # 👇 Format pesan otomatis ke WhatsApp
            phone = '6289671561543'
            message = f"Halo, saya ingin membeli:\n\n📦 *{product.name}*\n👕 Ukuran: *{size}*\n🔢 Jumlah: *{quantity}*\n💵 Total: *Rp {total:,}*"
            wa_url = f"https://wa.me/{phone}?text={quote(message)}"

            return redirect(wa_url)

    return render_template('checkout.html', product=product)

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

if __name__ == '__main__':
    with app.app_context():
        create_tables() 
    app.run(debug=True)
