from flask import render_template, url_for,jsonify,session,redirect,flash
import uuid
from datetime import datetime
from bookstore import app, excel
from bookstore import db, bcrypt, async_session, engine
from bookstore import mail
from bookstore.models import Book,Currency,Gener,User,Basket,BooksInBasket,Order,BooksInOrder,StatusOfOrder,Payment,Staff,TypeOfPayment
from bookstore.forms import RegistrationForm,LoginForm,SearchForm,GenerForm,BookForm,StaffForm,ReportForm,RoleUpdate
from bookstore.forms import UsernameUpdate,PasswordUpdate
from sqlalchemy.sql import text
from sqlalchemy import and_, or_, not_
from flask_mail import Message
from flask import request
import secrets
import os
import paypalrestsdk
from datetime import datetime
from PIL import Image
from time import sleep
from werkzeug.exceptions import abort
paypalrestsdk.configure({
  "mode": "sandbox", # sandbox or live
  "client_id": "AfTNzbMlmpqCzFxlPepARk1Li79atWwV9Qistl71utUfqpPze2zGMrTl2WNqMUjlGVgnBNyDbSdwX2vm",
  "client_secret": "EOWAVb72nB2qJgkzXuEKPIY68mw4IV8LbMEzL--NGludvtu3vw13PQVO2vPIYX0-U3ckxXz20PpoosUs" })

@app.errorhandler(400)
def handle_custom_exception(error):
    return render_template('error.html'), 400

@app.route("/books", methods=['GET', 'POST'])
def books():
    try:
        sForm = SearchForm(request.form)
        #fForm = FillerForm()
        page =  request.form.get('page')
        search =  request.form.get('search')
        if sForm.validate_on_submit():
            page = 1
        with db.engine.connect() as con:
                with con.begin():
                   data = con.execute(text("select * from books limit 50"))
        return render_template('books.html',user = None,sForm=sForm,data = data)
    except:
        abort(400)

@app.route("/book/<isbn>")
def book(isbn):
    try:
        sForm = SearchForm(request.form)
        return render_template('book.html',user = session.get('User'), sForm=sForm,book = Book.query.filter(Book.isbn == isbn).first())
    except:
        abort(400)

@app.route("/basket")
def basket():
    sForm = SearchForm(request.form)
    #print(session.get('User')['id'])
    basket =  basket = Basket.query.filter(Basket.id_user == session.get('User')['id']).first()
    total = 0
    for b in basket.books_in_basket:
        total = b.number_of_books*b.book.price
    return render_template('basket.html',user = session.get('User'),sForm=sForm,basket = basket,total = total/100)
@app.route("/basket/size")
def basket_size():
    b = Basket.query.filter(Basket.id_user == session['User']['id']).first()
    basket = BooksInBasket.query.filter(BooksInBasket.id_basket == b.id).count()
    return str(basket) 
@app.route("/basket/<isbn>",methods=['POST'])
def basket_add(isbn):
    basket = Basket.query.filter(Basket.id_user == session.get('User')['id']).first()
    if basket is None:
        db.session.add(Basket(id_user=session.get('User')['id'],creation_date = datetime.utcnow()))
        basket = Basket.query.filter(Basket.id_user == session.get('User')['id']).first()
    book = BooksInBasket.query.filter(and_(BooksInBasket.id_book == isbn, BooksInBasket.id_basket==basket.id)).first()
    if book is not None :
        book.number_of_books += 1
    else :
        basket.books_in_basket.append( BooksInBasket(id_basket = basket.id,id_book=isbn,number_of_books=1))
    db.session.commit()
    flash("Book was added to your basket")
    return redirect("/books")
@app.route("/basket/<isbn>/<amount>",methods=['POST'])
def basket_update(isbn,amount):
    basket = Basket.query.filter(Basket.id_user == session.get('User')['id']).first()
    book = BooksInBasket.query.filter(and_(BooksInBasket.id_book == isbn, BooksInBasket.id_basket==basket.id)).first()
    if int(amount) <= 0:
        db.session.delete(book)
    else:
        book.number_of_books = amount
    db.session.commit()
    return redirect("/basket")
@app.route('/order/<payment_type>',methods=['POST'])
def order(payment_type):
    basket = Basket.query.filter(Basket.id_user == session.get('User')['id']).first()
    if basket is not None:
        price = 0
        order = Order(id_user=session.get('User')['id'],creation_date = datetime.utcnow(),price = price, id_currency = 1,id_status = 1)     
        db.session.add(order) 
        
        for book in basket.books_in_basket:
            b = Book.query.filter( Book.id == book.id_book).first()
            if b.amount - book.number_of_books < 0:
                flash( 'Not enof books of {0}'.format(b.name))
                return redirect('/books')
            price = b.price *  book.number_of_books
            db.session.add(BooksInOrder(number_of_books= book.number_of_books, id_book = book.id_book, id_order = order.id, id_currency = 1, current_price = b.price))
        order.price = price
        BooksInBasket.query.filter( BooksInBasket.id_basket == basket.id).delete(synchronize_session='evaluate')
        db.session.delete(basket)
        db.session.commit()
        if payment_type == 1 :
            return redirect("/pay/{0}".format(order.id))
        payment_id = 'OD_{0}'.format(random_string())
        db.session.add(Payment(id = payment_id,time_of_creation = datetime.utcnow(), id_status = 1, payment_types =2))
        db.session.commit()
        order.id_payment = payment_id
        db.session.commit()
    flash('error basket is empty')
    return redirect('/basket')
@app.route("/pay/<id_order>",methods=['GET'])
def pay(id_order):
    order = Order.query.filter(Order.id == id_order).first()
    item = []
    for book in order.books_in_order:
        item.append({
                    "name": book.book.name,
                    "sku": book.id_book,
                    "price": book.current_price/100,
                    "currency": book.currency.name,
                    "quantity": book.number_of_books})
    print(item)
    print()
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"},
        "redirect_urls": {
            "return_url": "http://localhost:5000/execute",
            "cancel_url": "http://localhost:5000/cancel"},
        "transactions": [{
            "item_list": {
                "items": item},
            "amount": {
                "total": order.price/100,
                "currency": order.currency.name},
            }]})
    if payment.create():
        
        db.session.add(Payment(id = payment.id,time_of_creation = datetime.utcnow(), id_status = 1, payment_type =1))
        order.id_payment = payment.id
        db.session.commit()
        for link in payment.links:
            if link['rel'] == 'approval_url':
                return redirect(link['href'])
    
    print(payment.error)
    flash('error with payment')
    return redirect('/basket')
@app.route("/execute",methods = ['POST','GET'])
def execute():
    
    payment = paypalrestsdk.Payment.find(request.args['paymentId'])
    paymentB = Payment.query.filter(Payment.id == request.args['paymentId']).first()
    paymentB.id_status = 2
    db.session.commit()
    print()
    print(paymentB.id_status)
    print()
    db.session.commit()
    if payment.execute({'payer_id' : request.args['PayerID']}):
        flash('Payment has been made!')
        order = Order.query.filter(Order.id_payment == equest.args['paymentId'])
        order.id_status = 2
        db.session.commit()
        paymentB.id_status = 3
    else:
        flash('Error with payment has occured')
        paymentB.id_status = 4
        db.session.commit()
        print(payment.error)
    return redirect('/books')
@app.route("/cancel",methods = ['GET'])
def cancel(id_order):
    payment = Payment.query.filter(Payment.id == request.args['paymentId']).first()
    payment.id_status = 4
    db.session.commit()
    flash('error with pament has ocurred')
    return redirect('/basket')
@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            with db.engine.connect() as con:
                with con.begin():
                    queryU = """ insert into users(username,email,password,salt)
                                           values (:name,:email,MD5(CONCAT(:pass,:salt)),:salt) """
                    queryV = """ insert into validated_users(key,time_of_creation,valid,id_user)
                                           values (:key,:time,FALSE,:id_user)"""
                    parametersU = { 'name' : form.username.data,'email': form.email.data, 'pass': form.password.data, 'salt' : random_string(20) }
                    con.execute(text(queryU),parametersU)
                    us = User.query.order_by(User.id.desc()).first()
                    key = random_string(50)
                    parametersV = { 'key' : key, 'time': datetime.utcnow(), 'id_user' : us.id}
                    con.execute(text(queryV),parametersV)
        except:
            abort(400)
        send_verification_email(form.email.data,us.id,key)
        flash(f'Account created for {form.username.data}!', 'success')
        return "<h1>Check your email for verification</h1>"
    return render_template('register.html', title='Register', form=form)

@app.route("/verify/<ids>/<key>")
def verify(ids,key):
    with db.engine.connect() as con:
        query = """ update validated_users set valid = TRUE where id_user = :ids and key = :key"""
        params = {'ids' : ids , 'key' : key}
        con.execute(text(query),params)
        return "<h1>You have been verified</h1>"    
    
@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        
            query = """select users.id , username from users 
                       inner join validated_users on validated_users.id_user = users.id
                        where      validated_users.valid = TRUE
                          and      (username = :name or email = :name) 
                          and      MD5(CONCAT(:pass,salt)) = password"""   
            parameters = { 'name' : form.email.data, 'pass' : form.password.data}
            user = db.session.execute(query,parameters)
            #print(user.first())
            if  user.rowcount >= 1:
                session.permanent = True
                us = user.first()
                session['User'] = {'id':us['id'], 'name':us['username']}
                logger(user = us['id'], message = 'user(username/email): ' + us['username'] + ' logedin')
                flash('You have been logged in!', 'success')
                return redirect(url_for('books'))
                
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
                logger( message = 'user(username/email): ' + form.email.data + ' tried to login but failed')
                        
                
        
    return render_template('login.html', title='Login', form=form, backoffice = False)

@app.route("/logout")
def logout():
    session.pop('User')
    logger(user = session['Staff'].id, message = 'user: '+session['User'].id+' logedout ')
    return redirect(url_for('books'))

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)

@app.route("/backoffice-login", methods=['GET', 'POST'])
def backofficeLogin():
    form = LoginForm()
    
    if form.validate_on_submit():
        query = """select id , username from staff 
                    where     (username = :name or email = :name) 
                          and  MD5(CONCAT(:pass,salt)) = password"""   
        parameters = { 'name' : form.email.data, 'pass' : form.password.data}
        user = db.session.execute(query,parameters)
            
        if  user.rowcount == 1:
            session.permanent = True
            us = user.first()
            session['Staff'] = {'id':us['id'], 'name':us['username']}
            logger(user = us['id'],message = 'staff(username): '+ us['username'] + ' loged in')
            flash('You have been logged in!', 'success')
            return redirect(url_for('backoffice'))
        else:

            logger(message = 'staff(username):'+ form.email.data + 'tried to login but failed')
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form, backoffice = True)
@app.route("/backoffice-logout")
def backoffice_logout():
    logger(user = session['Staff'].id, message = 'staff: '+session['Staff'].id+' logedout ')
    session.pop('Staff')
    return redirect('/backoffice-login')
@app.route("/backoffice")
def backoffice():
    if session['Staff']:
        return render_template('backoffice.html',title='backoffice',staff = session['Staff'])
    return "<h1> Please LogIn </h1>"

@app.route('/backoffice-geners')
def geners():
    if session['Staff']:
        if not has_permition('read_geners'):
            flash('no permition')
            return redirect('/backoffice')
        return render_template('geners.html',title='geners', pers = [has_permition('create_geners'),has_permition('update_geners'),has_permition('delete_geners')] ,staff = session['Staff'],geners = Gener.query.all())
    return "<h1> Please LogIn </h1>"

@app.route('/add-gener',methods=['GET','POST'])
def add_geners():
    if session['Staff'] is not None :
        form = GenerForm()
        if form.validate_on_submit():
            if not has_permition('create_geners'):
                flash(f'no permition')
                return redirect('/backoffice-geners')
            gener = Gener(name=form.name.data)
            db.session.add(gener)
            db.session.commit()
            flash(f'Added gener!', 'success')
            return redirect('/backoffice-geners')

        return render_template('add-geners.html',form = form,title='add-geners', staff = session['Staff'])
    return "<h1> Please LogIn </h1>"

@app.route('/update-gener/<id>',methods=['GET','POST'])
def update_geners(id):
    if session['Staff'] is not None :
        form = GenerForm()
        gener  = Gener.query.filter(Gener.id == id).first()
        if form.validate_on_submit():
            if not has_permition('update_geners'):
                flash(f'no permition')
                return redirect('/backoffice-geners')
            gener.name = form.name.data
            db.session.commit()
            flash(f'Added gener!', 'success')
            return redirect('/backoffice-geners')

        return render_template('update-gener.html',gener = gener,form = form,title='add-geners', staff = session['Staff'])
    return "<h1> Please LogIn </h1>"

@app.route('/delete-gener/<id>',methods=['GET','POST'])
def delete_geners(id):
    if session['Staff'] is not None :
        if not has_permition('delete_geners'):
                flash(f'no permition')
                return redirect('/backoffice-geners')
        gener  = Gener.query.filter(Gener.id == id).first()
        db.session.delete(gener)
        db.session.commit()
        flash(f'Deleted gener!', 'success')
        return redirect('/backoffice-geners')
    return "<h1> Please LogIn </h1>"

@app.route('/backoffice-books',methods=['GET'])
def b_books():
    if session['Staff']:
        if not has_permition('read_books'):
            flash('no permition')
            return redirect('/backoffice')
        page = request.form.get('page') if 'page' not in request.form else 1
        fil = True
        if request.args.get('name') is not None:
            fil = and_(fil,Book.name.contains(request.args.get('name')))
        if request.args.get('autor') is not None:
            fil = and_(fil,Book.autor.contains(request.args.get('autor')))
        if request.args.get('lower') is not None and request.args.get('lower') != '':
            fil = and_(fil,Book.price <= float(request.args.get('lower'))*100)
        if request.args.get('upper') is not None and request.args.get('upper') != '':
            fil = and_(fil,Book.price >= float(request.args.get('upper'))*100)
        if request.args.get('gener') is not None and request.args.get('gener') != '':
            fil = and_(fil,Book.id_gener == int(request.args.get('gener')))
        return render_template('b-books.html',
                                values = {
                                    'name': request.args.get('name') if request.args.get('name') is not None else '',
                                    'autor': request.args.get('autor') if request.args.get('autor') is not None else '',
                                    'gener': int(request.args.get('gener')) if request.args.get('gener') is not None else '',
                                    'upper': request.args.get('upper') if request.args.get('upper') is not None else '',
                                    'lower': request.args.get('lower') if request.args.get('lower') is not None else '',
                                },
                                title='books', 
                                geners = Gener.query.all(),
                                pers = [has_permition('create_books'),
                                        has_permition('update_books'),
                                        has_permition('delete_books')],  
                                staff = session['Staff'],
                                books = Book.query.filter(fil).paginate(page=page,per_page=5))
    return "<h1> Please LogIn </h1>"

@app.route('/add-book',methods=['GET','POST'])
def add_books():
    if session['Staff'] is not None :
        
            form = BookForm()
            form.gener.choices = [(g.id, g.name) for g in Gener.query.order_by('id').all()]
            form.currency.choices = [(g.id, g.name) for g in Currency.query.order_by('id').all()]
       
            if form.validate_on_submit():
                if not has_permition('create_books'):
                        logger(user=session['Staff'].id,message= 'staff: '+session['Staff'].username+' tried to add a book but has no permition')
                        flash(f'no permition')
                        return redirect('/backoffice-books')
                cover_file = save_picture(form.cover.data)
                book = Book(isbn = form.isbn.data,
                            id = 1010101010,
                            name=form.name.data,
                            autor=form.autor.data,
                            price=form.price.data*100,
                            discount=form.discount.data*100,
                            description = form.description.data,
                            amount = form.amount.data,
                            cover = cover_file, 
                            id_gener = form.gener.data,
                            id_currency = form.currency.data)
                db.session.add(book)
                db.session.commit()
                flash(f'Added book!', 'success')
                return redirect('/backoffice-books')

            return render_template('add-book.html',form = form,title='add-geners', staff = session['Staff'])
        
    return "<h1> Please LogIn </h1>"

@app.route('/update-book/<isbn>',methods=['GET','POST'])
def update_books(isbn):
    
    if session['Staff'] is not None :
        form = BookForm()
        book  = Book.query.filter(Book.isbn == isbn).first()
        form.gener.choices = [(g.id, g.name) for g in Gener.query.order_by('id').all()]
        form.gener.default = book.gener.id
        form.currency.choices = [(g.id, g.name) for g in Currency.query.order_by('id').all()]
        form.currency.default = book.currency.id
        form.description.default = book.description
        if form.validate_on_submit():
            if not has_permition('update_books'):
                    logger(user=session['Staff'].id,message= 'staff: '+session['Staff'].username+' tried to updated a book but has no permition')
                    flash(f'no permition')
                    return redirect('/backoffice-books') 
            if form.cover.data:
                book.cover = save_picture(form.cover.data)
            if form.description.data:
                book.description = save_picture(form.description.data)
            book.autor=form.autor.data
            book.price=form.price.data*100
            book.discount=form.discount.data*100
            book.amount = form.amount.data
            book.id_gener = form.gener.data
            book.id_currency = form.currency.data
            book.name = form.name.data
            db.session.commit() 
            logger(user=session['Staff'].id,message= 'staff: '+session['Staff'].username+' updated book with id: '+ isbn)
            flash(f'Updated book!', 'success')
            return redirect('/backoffice-books')

        return render_template('update-book.html',book = book,form = form,title='update-books', staff = session['Staff'])
    return "<h1> Please LogIn </h1>"

@app.route('/delete-book/<isbn>',methods=['GET','POST'])
def delete_books(isbn):
    if session['Staff'] is not None :
        if not has_permition('delete_books'):
                    flash(f'no permition')
                    return redirect('/backoffice-books')
        book  = Book.query.filter(Book.isbn == isbn).first()
        db.session.delete(book)
        db.session.commit()
        flash(f'Deleted gener!', 'success')
        return redirect('/backoffice-geners')
    return "<h1> Please LogIn </h1>"

@app.route('/backoffice-staff')
def staff():
    if session['Staff']:
        if not has_permition('read_staff'):
            flash('no permition')
            return redirect('/backoffice')
        return render_template('staff.html',title='staff', staff = session['Staff'], pers = [has_permition('create_staff'),has_permition('update_staff'),has_permition('delete_staff')],staffs = Staff.query.all())
    return "<h1> Please LogIn </h1>"

@app.route('/add-staff',methods=['GET','POST'])
def add_staff():
    if session['Staff'] is not None :
        form = StaffForm()
       
        if form.validate_on_submit():
            if not has_permition('create_staff'):
                    flash(f'no permition')
                    logger(user=session['Staff'].id,message= 'staff: '+session['Staff'].username+' tried to add staff  but has no permitionsto do so.')        
                    return redirect('/backoffice-staff')
            with db.engine.connect() as con:
                query = """insert into staff(username,email,password,salt)
                                values (:name,:email,MD5(CONCAT(:pass,:salt)),:salt)"""
                parameters = { 'name' : form.username.data,'email': form.email.data, 'pass': form.password.data, 'salt' : random_string(20) }
                con.execute(text(query),parameters)
            logger(user=session['Staff']['id'],message= 'staff: '+session['Staff']['name']+' added  staff with username:' + form.username.data)        
            flash(f'Added staff!', 'success')
            return redirect('/backoffice-staff')

        return render_template('add-staff.html',form = form,title='add-geners', staff = session['Staff'])
    return "<h1> Please LogIn </h1>"

@app.route('/update-staff/<id>',methods=['GET','POST'])
def update_staff(id):
    
    if session['Staff'] is not None :
        formU = UsernameUpdate()
        formP = PasswordUpdate()
        formR = RoleUpdate()
        staff  = Staff.query.filter(Staff.id == id).first()
        if formU.validate_on_submit():
            if not has_permition('update_staff'):
                    logger(user=session['Staff'].id,message= 'staff: '+session['Staff'].username+' tried to update staff  but has no permitionsto do so.')        
                    flash(f'no permition')
                    return redirect('/backoffice-staff')        
            staff.email = formU.email.data
            staff.name = formU.username.data 
            db.session.commit()
            flash(f'Updated staff!', 'success')
            return redirect('/update-staff/{0}'.format(id))
        if formP.validate_on_submit():        
            with db.engine.connect() as con:
                query = """update staff set password = MD5(CONCAT(:pass,:salt)), salt = :salt  where id = :id"""
                parameters = { 'pass': formP.password.data, 'salt' : random_string(20) , 'id':id}
                con.execute(text(query),parameters)
            print()
            print(session['Staff']["id"])                                  
            print()
            logger(user=session['Staff']["id"],message= 'staff: '+session['Staff']["name"]+' updated password of staff with id:' + id)        
            flash(f'Updated staff!', 'success')
            return redirect('/update-staff/{0}'.format(id))
        if formR.validate_on_submit():
            with db.engine.connect() as con:
                with con.begin():
                    role = con.execute(text('select id from roles where name = :role'),{'role':formR.name.data}).first()
                    query = """insert into roles_of_staff(id_staff,id_role) values (:staff,:role)"""
                    parameters = { 'staff': int(id), 'role' : role[0]}
                    con.execute(text(query),parameters)
            print()
            print(session['Staff'])                                  
            print()
            logger(user=session['Staff']["id"],message= 'staff: '+session['Staff']["name"]+' updated username/email of staff with id:' + id)        
            flash(f'Updated staff!', 'success')
            return redirect('/update-staff/{0}'.format(id))
        roles = []
        with db.engine.connect() as con:
                roles = con.execute(text("""select roles.id,roles.name from roles 
                                            inner join roles_of_staff on roles_of_staff.id_role = roles.id
                                            where roles_of_staff.id_staff = :staff"""),{'staff':id}).all() 
        roles = roles if roles is not None else []     
        
        return render_template('update-staff.html',book = book,formU = formU,formR=formR,roles = roles,staf = staff,formP = formP,title='update-books', staff = session['Staff'])
    return "<h1> Please LogIn </h1>"

@app.route('/delete-staff/<id>',methods=['GET','POST'])
def delete_staff(id):
    if session['Staff'] is not None :
        if not has_permition('delete_staff'):
                    flash(f'no permition')
                    return redirect('/backoffice-staff')
        staff  = Staff.query.filter(Staff.id == id).first()
        db.session.delete(staff)
        db.session.commit()
        flash(f'Deleted staff!', 'success')
        return redirect('/backoffice-staff')
    return "<h1> Please LogIn </h1>"

@app.route('/backoffice-users',methods=['GET','POST'])
def user():
   
    
    if session['Staff']:
        if not has_permition('read_users'):
            flash('no permition')
            return redirect('/backoffice')
        page = request.form.get('page') if 'page' not in request.form else 1
        fil = True
        if request.args.get('name') is not None:
            fil = and_(fil,User.username.contains(request.args.get('name')))
        return render_template('users.html', 
                                pers = [has_permition('create_users'),
                                        has_permition('update_users'),
                                        has_permition('delete_users')],
                                title='user', 
                                staff = session['Staff'],
                                users = User.query.filter(fil).paginate(page=page,per_page=5),
                                en = request.args.get('name'))
    return "<h1> Please LogIn </h1>"
@app.route('/sugestions/users/<name>',methods=['GET'])
def sugestions_user(name):
    with db.engine.connect() as con:
        query = 'select username from users where Position( :name  in username ) = 1 limit 5'
        parameters = {'name' : name}
        rows = con.execute(text(query),parameters).all()
        data = [ row.username for row in rows]
    return jsonify(data)
@app.route('/add-user',methods=['GET','POST'])
def add_user():
    if session['Staff'] is not None :
        form = StaffForm()
       
        if form.validate_on_submit():
            if not has_permition('create_users'):
                    flash(f'no permition')
                    return redirect('/backoffice-users')
            with db.engine.connect() as con:
                query = """insert into users(username,email,password,salt)
                                values (:name,:email,MD5(CONCAT(:pass,:salt)),:salt)"""
                parameters = { 'name' : form.username.data,'email': form.email.data, 'pass': form.password.data, 'salt' : random_string(20) }
                con.execute(text(query),parameters)
                us = User.query.order_by(User.id.desc()).first()
                queryV = """ insert into validated_users(key,time_of_creation,valid,id_user)
                            values (:key,:time,TRUE,:id_user)"""
                key = random_string(50)
                parametersV = { 'key' : key, 'time': datetime.utcnow(), 'id_user' : us.id}
                con.execute(text(queryV),parametersV)
            flash(f'Added user!', 'success')
            return redirect('/backoffice-user')

        return render_template('add-user.html',form = form,title='add-geners', staff = session['Staff'])
    return "<h1> Please LogIn </h1>"

@app.route('/update-user/<id>',methods=['GET','POST'])
def update_user(id):
    
    if session['Staff'] is not None :
        formU = UsernameUpdate()
        formP = PasswordUpdate()
        user  = User.query.filter(User.id == id).first()
        if formU.validate_on_submit():
            if not has_permition('update_users'):
                    flash(f'no permition')
                    return redirect('/backoffice-users')        
            user.email = formU.email.data
            user.name = formU.username.data 
            db.session.commit()
            flash(f'Updated user!', 'success')
            return redirect('/update-user/{0}'.format(id))
        if formP.validate_on_submit():        
            with db.engine.connect() as con:
                query = """update user set password = MD5(CONCAT(:pass,:salt)), salt = :salt  where id = :id"""
                parameters = { 'pass': formP.password.data, 'salt' : random_string(20) , 'id':id}
                con.execute(text(query),parameters)
            flash(f'Updated user!', 'success')
            return redirect('/update-user/{0}'.format(id))

        return render_template('update-user.html',book = book,formU = formU,user = user,formP = formP,title='update-books', staff = session['Staff'])
    return "<h1> Please LogIn </h1>"

@app.route('/delete-user/<id>',methods=['GET','POST'])
def delete_user(id):
    if session['Staff'] is not None :
        if not has_permition('delete_users'):
                    flash(f'no permition')
                    return redirect('/backoffice-users')
        user  = User.query.filter(User.id == id).first()
        db.session.delete(user)
        db.session.commit()
        flash(f'Deleted user!', 'success')
        return redirect('/backoffice-user')
    return "<h1> Please LogIn </h1>"

@app.route('/backoffice-orders',methods = ['GET','POST'])
def orders():
    if session['Staff']:
        if not has_permition('read_orders'):
            flash('no permition')
            return redirect('/backoffice')
        page = request.form.get('page') if 'page' not in request.form else 1
        fil = True
        if request.args.get('name') is not None and request.args.get('name') != '':
            fil = and_(fil,Order.user.username == request.args.get('name'))
        if request.args.get('lowerPrice') is not None and request.args.get('lowerPrice') != '':
            fil = and_(fil,Order.price <= float(request.args.get('lowerPrice'))*100)
        if request.args.get('upperPrice') is not None and request.args.get('upperPrice') != '':
            fil = and_(fil,Order.price >= float(request.args.get('upperPrice'))*100)
        if request.args.get('lowerDate') is not None and request.args.get('lowerDate') != '':
            fil = and_(fil,Order.creation_date <= datetime.strptime(request.args.get('lowerDate'),'%Y-%m-%d'))
        if request.args.get('upperDate') is not None and request.args.get('upperDate') != '':
            fil = and_(fil,Order.creation_date >= datetime.strptime(request.args.get('upperDate'),'%Y-%m-%d'))
        if request.args.get('status') is not None and request.args.get('status') != '':
            fil = and_(fil,Order.id_status == int(request.args.get('status')))
        return render_template('orders.html',
                                values = {
                                    'name': request.args.get('name') if request.args.get('name') is not None else '',
                                    'status': int(request.args.get('status')) if request.args.get('status') is not None else '',
                                    'upperPrice': request.args.get('upperPrice') if request.args.get('upperPrice') is not None else '',
                                    'lowerPrice': request.args.get('lowerPrice') if request.args.get('lowerPrice') is not None else '',
                                    'uperDate': request.args.get('upperDate') if request.args.get('upperDate') is not None else '',
                                    'lowerDate': request.args.get('lowerDate') if request.args.get('lowerDate') is not None else '',
                                },
                                title='orders', 
                                statuses = StatusOfOrder.query.all(),
                                pers = [has_permition('create_orders'),
                                        has_permition('update_orders'),
                                        has_permition('delete_orders')],  
                                staff = session['Staff'],
                                orders = Order.query.filter(fil).order_by(Order.creation_date.desc()).paginate(page=page,per_page=5))
    return "<h1> Please LogIn </h1>"

@app.route('/udate-order/<id>',methods=['GET'])
def update_order(id):
    return render_template('add-order.html')

@app.route('/add-order',methods=['GET'])
def add_order():
    return render_template('add-order.html',statuses = StatusOfOrder.query.order_by().all(), staff = session['Staff'], title='orders')

@app.route('/add-order',methods=['POST'])
def add_order_p():
      with db.engine.connect() as con:
            prices = request.form.getlist('prices[]')
            isbns = request.form.getlist('isbns[]')
            amounts =  request.form.getlist('amounts[]')
            user = User.query.filter(User.username ==  request.form.get('user')).first()
            if user is None:
                return 'User does not exist'
            price = 0
            for p in range(0,len(prices)):
                price += price + float(prices[p])*int(amounts[p])
            print()
            print(price)
            print()
            con.execute(text('''insert into orders(id_user,id_status,creation_date,price,id_currency,id_payment)
                                values ( :user , :status , :date , :price ,1,null)'''),{'user':user.id,
                                                                                        'status':int(request.form.get('status')),
                                                                                        'date':datetime.strptime(request.form.get('date'),'%Y-%m-%dT%H:%S'),
                                                                                        'price': price*100})
            order = Order.query.order_by(Order.id.desc()).first().id
            for p in range(0,len(isbns)):
              con.execute(text('''insert into books_in_order(id_order,id_book,current_price,number_of_books,id_currency)
                                  values ( :order , :book , :price , :amount ,1)'''),{'order':order,
                                                                                      'book': Book.query.filter(Book.isbn == isbns[p]).first().id,
                                                                                      'price':float(prices[p])*100,
                                                                                      'amount':int(amounts[p])})
            
            return 'Added Order'
@app.route('/delete-order/<id>',methods=['GET'])
def delete_order(id):
    with db.engine.connect() as con:
        con.excute(text('delete from books_in_order where id_order = :order'),{'order':id})
        con.excute(text('delete from orders where id = :order'),{'order':id})
    return 'order has been deleted'



@app.route('/report',methods=['GET','POST'])
def report():
    form = ReportForm()
    data = None
    total = 0.0
    form.status.choices = [(g.id, g.name) for g in StatusOfOrder.query.order_by('id').all()]
    form.status.choices.insert(0,(0,''))
    form.paymentType.choices = [(g.id, g.name) for g in TypeOfPayment.query.order_by('id').all()]
    form.paymentType.choices.insert(0,(0,''))
    if form.validate_on_submit():
            data = reportFun(form)
            total = data[1]
            data = data[0]
            messageForLog = 'staff: ' + session['Staff'].username + 'made a report with parameter:\n'

            logged(user = session['Staff'].id, message = messageForLog)
            if form.tocsv.data:
                par = []
                cols = []
                period = {
                    'none': 'None',
                    'MM-DD': 'Day',
                    'IW':'Weak',
                    'MM':'Month',
                    ' ':'Year'
                 }
                if form.period.data != 'none':
                    cols.append('period')
                if form.userShow.data != 'True':
                    cols.append('user')
                if form.statusShow.data != 'True':
                    cols.append('status')
                if form.paymentTypeShow != 'True':
                    cols.append('payment')
                cols.append('number of items')
                cols.append('sum')
                cols.append('currency')
                par.append(['Period Type',period[form.period.data]])
                if  form.fromDate.data is None:
                    par.append(['From Date',str(Order.query.order_by(Order.creation_date.asc()).first().creation_date)])
                else:
                    par.append(['From Date',form.fromDate.data])
                if  form.toDate.data is None:
                    par.append(['To Date',str(Order.query.order_by(Order.creation_date.desc()).first().creation_date)])
                else:
                    par.append(['To Date',form.toDate.data])
                par.append(['Users Show:',form.userShow.data])
                if form.user.data is not None and form.user.data != '' :
                    par.append(['Status of Order:',form.user.data])
                par.append(['Status of Order Show:',form.statusShow.data])
                if form.status.data is not None and form.status.data != '0' :
                    par.append(['Status of Order:',StatusOfOrder.query.filter(StatusOfOrder.id == int(form.status.data)).first().name])
                par.append(['Status of Order Show:',form.paymentTypeShow.data])
                if form.paymentType.data is not None and form.paymentType.data != '0':
                    par.append(['Type Of Payment:',TypeOfPayment.query.filter(TypeOfPayment.id == int(form.paymentType.data)).first().name])
                rep = [*par,[],cols,*[[s for s in p] for p in data]]
                return excel.make_response_from_array(rep,'xlsx')
    return render_template('report.html',data=data, total = total,form = form,title='update-books', staff = session['Staff'])


    

def reportFun(form):
    with db.engine.connect() as con:
            query = """select """
            queryT = """select round(sum(price)/cast(currency.devision as decimal),2) as sum,  currency.name as currency
                            from orders inner join currency on currency.id = orders.id_currency
                                        inner join users on orders.id_user = users.id
                                        inner join status_of_order on status_of_order.id=orders.id_status 
                                     """
            if form.period.data != 'none':
                query += "to_char(creation_date, :period) as period ,"
            if form.userShow.data == 'True' :
                query += "users.username as user, "
            if form.paymentTypeShow.data == 'True' :
                query += "payment_types.name as type, "
            if form.statusShow.data == 'True':
                query += "status_of_order.name as status, "
                queryT += """inner join payments on payments.id = orders.id_payment
                            inner join payment_types on payment_types.id = payments.payment_types"""
            queryT += " where True"    
            query += 'count(*) as count, round(sum(price)/cast(currency.devision as decimal),2) as sum, currency.name as currency '
            query += ' from orders inner join currency on currency.id = orders.id_currency'
            if form.userShow.data == 'True':
                query += " inner join users on users.id=orders.id_user "
            if form.statusShow.data == 'True':
                query += " inner join status_of_order on status_of_order.id=orders.id_status "
            if form.paymentTypeShow.data == 'True' :
                query+= """ inner join payments on payments.id = orders.id_payment
                            inner join payment_types on payment_types.id = payments.payment_types """    
            query += ' where True '
            if form.statusShow.data == 'True' and (form.status.data and form.status.data != '0'):
                query += ' and orders.id_status = :status '
                queryT += ' and orders.id_status = :status '
            if form.userShow.data == 'True' and form.user.data:
                query += ' and users.username = :name '
                queryT += ' and users.username = :name '    
            if form.paymentTypeShow.data == 'True'  and (form.paymentType.data and form.paymentType.data != '0'):
                query += ' and payments.payment_types = :type '
                queryT += ' and payments.payment_types = :type '   
            if form.fromDate.data:
                query += " and orders.creation_date >= :fromDate ::timestamp with time zone at time zone '+03'"
                queryT += " and orders.creation_date >= :fromDate ::timestamp with time zone at time zone '+03'"
            if form.toDate.data:
                query += " and orders.creation_date <= :toDate ::timestamp with time zone at time zone '+03'"
                queryT += " and orders.creation_date <= :toDate ::timestamp with time zone at time zone '+03'"
            
            query+= " group by currency.name, currency.devision"
            queryT+= " group by currency.name, currency.devision"
            if form.period.data != 'none':
               query+=', period'
            if form.userShow.data == 'True' :
                query+= ', users.username'
            if form.statusShow.data == 'True':
                query+= ', status_of_order.name'
            if form.paymentTypeShow.data == 'True':
                query+= ', payment_types.name'
            if form.period.data != 'none':
                query+= ' order by period'
            parameters = {'type':form.paymentType.data,
                          'status':form.status.data,
                          'name': form.user.data ,
                          'period': "IYYY" + (' ' if form.period.data == ' ' else '-' + form.period.data),   
                          'toDate': form.toDate.data,
                          'fromDate': form.fromDate.data}
            data =  con.execute(text(query),parameters).all() 
            total = con.execute(text(queryT),parameters).all()
            total =  total[0] if total else 0
            return [data,total] 


@app.route('/roles',methods=['GET','POST'])
def roles():
    if not has_permition('read_roles'):
            flash('no permition')
            return redirect('/backoffice')
    data = []
    with db.engine.connect() as con:
        data = con.execute('select id, name from roles').all()
    return render_template('roles.html',data=data,title='update-roles',  pers = [has_permition('create_roles'),has_permition('update_roles'),has_permition('delete_roles')],staff = session['Staff'])
@app.route('/add-role',methods=['GET','POST'])
def add_role():
    form = GenerForm()
    if form.validate_on_submit():
        if not has_permition('create_roles'):
            flash(f'no permition')
            return redirect('/roles')
        with db.engine.connect() as con:
            con.execute(text('insert into roles(name) values (:name)'),{'name':form.name.data})
        flash('added a role')
        return redirect('/roles')
    return render_template('add-role.html',form=form,title='update-books', staff = session['Staff'])
@app.route('/permitions-role/<id>',methods=['GET'])
def permitions(id):
    data = []
    if not has_permition('read_roles'):
                    flash(f'no permition')
                    return redirect('/roles')
    with db.engine.connect() as con:
        data =    con.execute(text('select id_permition from  permitions_for_role where id_role = :id order by id_permition'),{'id':id})
        pl = con.execute(text('select substring(name,8) as s  from permitions where mod(id,4)=0')).all()
        data = [ d[0] for d in data]
        stc = [(p[0],[i[0] for i in con.execute(text('select id  from permitions where substring(name,8)=:sub or substring(name,6)=:sub'),{'sub':p[0]}).all()]) for p in pl]
    return  render_template('permitions.html',role = id,data=data,per = stc,title='update-books', staff = session['Staff']) 
@app.route('/remove-permition',methods=['POST'])
def remove_permition():
    if not has_permition('update_roles'):
        return 'has no permition'
    with db.engine.connect() as con:
        con.execute(text('delete from permitions_for_role where id_permition =:permition and id_role = :role'),{"permition":request.values['permition'],"role":request.values['role'],})
    return 'Permitions was revoked'
@app.route('/add-permition',methods=['POST'])
def add_permition():
    if not has_permition('update_roles'):
        return 'has no permition'
    with db.engine.connect() as con:
        con.execute(text('insert into permitions_for_role(id_role,id_permition) values (:role,:permition)'),{"permition":request.values['permition'],"role":request.values['role'],})
    return 'Permitions was added'
@app.route('/permition-read',methods=['GET'])
def permitions_read():
    st = ''
    if  has_permition('read_books'):
        st = st +'<li class="nav-item"><a class="nav-link" href="/backoffice-books">Books</a></li>'
    if  has_permition('read_geners'):
        st = st +'<li class="nav-item"><a class="nav-link" href="/backoffice-geners">Geners</a></li>'
    if  has_permition('read_users'):
        st = st +'<li class="nav-item"><a class="nav-link" href="/backoffice-users">Users</a></li>'
    if  has_permition('read_orders'):
        st = st +'<li class="nav-item"><a class="nav-link" href="/backoffice-orders">Orders</a></li>'
    if  has_permition('read_staff'):
        st = st +'<li class="nav-item"><a class="nav-link" href="/backoffice-staff">Staff</a></li>'
    if  has_permition('read_roles'):
        st = st +'<li class="nav-item"><a class="nav-link" href="/roles">Roles</a></li>'
    st = st +'<li class="nav-item"><a class="nav-link" href="/report">Report</a></li>'
    st = st +'<li class="nav-item"><a class="nav-link" href="/backoffice-logout">LogOut</a></li>'
    return st
@app.route('/revoke-role/<staff>/<role>',methods=['GET'])
def revoke_role(staff,role):
    if not has_permition('update_staff'):
        flash(f'no permition')
        return redirect('/update-staff/{0}'.format(staff))
    with db.engine.connect() as con:
        con.execute(text('delete from roles_of_staff where id_staff= :staff and id_role = :role'),{'staff':staff,'role':role})
    flash(f'Updated staff!!!','succes')
    return redirect('/update-staff/{0}'.format(staff))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='angelsedmakov@gmail.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
                {url_for('reset_token', token=token, _external=True)}
                    If you did not make this request then simply ignore this email and no changes will be made.
                '''
    mail.send(msg)


def send_verification_email(email,id,key):
    try:
        msg = Message('validation Request',
                      sender='angelsedmakov@gmail.com',
                      recipients=[email])
        msg.body = f'''To reset your password, visit the following link:
                    {url_for('verify', id=id,key = key, _external=True)}
                        If you did not make this request then simply ignore this email and no changes will be made.
                    '''
        mail.send(msg)
    except:
        abort(400)
def logger(message,user = None):
    
        with db.engine.connect() as con:
            with con.begin():
                con.execute(text("""insert into actions(user_id,action,time) 
                                    values (:user,:message,now())  """),
                                    {'message': message,
                                     'user'    : user })
    
                
def save_picture(form_picture):
    picture_path = os.path.join(app.root_path,'static/images/',form_picture.filename)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return 'static/images/'+form_picture.filename

def random_string(string_length=10):
    random = str(uuid.uuid4()) 
    random = random.upper() 
    random = random.replace("-","") 
    return random[0:string_length] 

def has_permition(permition_name):
    has = False 
    with db.engine.connect() as con:
        has = True if con.execute(text("""select permitions_for_role.id from permitions_for_role
                                           inner join permitions on permitions.id = permitions_for_role.id_permition 
                                           inner join roles on permitions_for_role.id_role = roles.id
                                           inner join roles_of_staff on roles.id = roles_of_staff.id_role 
                                        where permitions.name = :permition 
                                          and roles_of_staff.id_staff = :staff """),
                                        {"permition": permition_name,
                                         "staff": session['Staff']['id']}).first() is not None else False
        print(has)
    return has 