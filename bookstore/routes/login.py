
@app.route("/books", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def books():
    
    sForm = SearchForm(request.form)
    #fForm = FillerForm()
    fil = True
    page = request.form.get('page')
    search = request.form.get('search')
    print(search)
    if sForm.validate_on_submit():
        page = 1
    if search is not None:
        fil = and_(fil,or_(or_(Book.name.contains(sForm.search.data.upper()),Book.autor.contains(sForm.search.data),Book.isbn.contains(sForm.search.data))))
    return render_template('books.html',user = session.get('User'),sForm=sForm,data =  Book.query.filter(fil).paginate(page=page,per_page=24))  
