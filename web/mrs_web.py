#   importing necessary libraries

from csv import excel_tab
#from imp import release_lock
from flask import Flask,render_template,request,session,redirect,jsonify
import pandas as pd
import pickle
import sqlite3
from flask_session import Session
import requests

#   creating object for Flask class

mrs=Flask(__name__)

#   setting up a session

mrs.config["SESSION_PERMANENT"] = False
mrs.config["SESSION_TYPE"] = "filesystem"
Session(mrs)

#   loading pickle files

movies_dict=pickle.load(open('../movies_dict.pkl','rb'))
movies=pd.DataFrame(movies_dict)
similarity=pickle.load(open('../similarity.pkl','rb'))


a=[]
fetch_id=[]
poster=[]
homepage=[]
overview=[]
all=[]
vote_avg=[]
release_date=[]

all_mov=[]
all_mov_poster=[]
all_mov_title=[]
all_mov=movies['movie_id'][1:31]
all_mov_title=movies['title'][1:31]
all_mov_link=[]
for i in all_mov:
    response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=94477f90c8a637166a3eeff4a7712b96&language=en-US'.format(i))
    data=response.json()
    all_mov_poster.append("https://image.tmdb.org/t/p/w500/"+data['poster_path'])
    all_mov_link.append(data['homepage'])


movie_index=movies[['title']].index[0]
distances=similarity[movie_index]
movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])
for i in movies_list:
    all.append(movies.iloc[i[0]].title)

#   movie recommendation code

def recommend(movie):
    movie_index=movies[movies['title']==movie].index[0]
    distances=similarity[movie_index]
    movies_list=sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]
    for i in movies_list:
        a.append(movies.iloc[i[0]].title)
        fetch_id.append(movies.iloc[i[0]].movie_id)

l=len(movies['movie_id'])

#   fxn for history extraction

excel_mov_name=[]
excel_mov_id=[]
excel_mov_poster=[]
excel_mov_link=[]
excel_mov_over=[]
excel_mov_vote_avg=[]
excel_mov_release_date=[]
def exact_mov(movie):
    movie_index=movies[movies['title']==movie].index[0]
    for i,j in zip(movies['title'],movies['movie_id']):
        if i==movie:
            if i not in excel_mov_name:
                excel_mov_name.append(i)
                excel_mov_id.append(j)


hist_name=[]
hist_id=[]
hist_poster=[]
hist_link=[]
def hist_mov(movie):
    movie_index=movies[movies['title']==movie].index[0]
    for i,j in zip(movies['title'],movies['movie_id']):
        if i==movie:
            hist_name.append(i)
            hist_id.append(j)  
    print(hist_name) 

#   home page history render code

@mrs.route('/',methods=["POST","GET"])
def index():
    a.clear() 
    fetch_id.clear()
    poster.clear()
    homepage.clear()
    excel_mov_name.clear()
    excel_mov_id.clear()
    excel_mov_poster.clear()

    rec=request.args.get("recommend")
    con=sqlite3.connect('MRS.db')
    c=con.cursor()
    if(request.method=='POST' or session['uname']!=None):
        c.execute(f"select key from history where uname='{session['uname']}' ")
        rows = c.fetchall()
        for i in rows:
            exact_mov(i[0])
        for i in excel_mov_name:
            recommend(i)
        con.commit()
        con.close()  

        for i in fetch_id:
            response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=94477f90c8a637166a3eeff4a7712b96&language=en-US'.format(i))
            data=response.json()
            poster.append("https://image.tmdb.org/t/p/w500/"+data['poster_path'])
            homepage.append(data['homepage'])
        for i in excel_mov_id:
            response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=94477f90c8a637166a3eeff4a7712b96&language=en-US'.format(i))
            data=response.json()
            excel_mov_poster.append("https://image.tmdb.org/t/p/w500/"+data['poster_path'])
            excel_mov_link.append(data['homepage'])
        return render_template('index.html',mov=movies,l=l,fetch_id=fetch_id,recc=list(zip(a,poster,homepage)),excel_mov=list(zip(excel_mov_name,excel_mov_poster,excel_mov_link))
        ,all_mov_list=list(zip(all_mov_title,all_mov_poster,all_mov_link)))
    else:
        return render_template('index.html',mov=movies,l=l,fetch_id=fetch_id,recc=list(zip(a,poster,homepage)),excel_mov=list(zip(excel_mov_name,excel_mov_poster,excel_mov_link))
        ,all_mov_list=list(zip(all_mov_title,all_mov_poster,all_mov_link)))
        
        #return render_template("register.html")


#   contact code
@mrs.route('/contact')
def contact():
    return render_template('contact.html',mov=movies,l=l,fetch_id=fetch_id,recc=list(zip(a,poster,homepage)),excel_mov=list(zip(excel_mov_name,excel_mov_poster,excel_mov_link))
        ,all_mov_list=list(zip(all_mov_title,all_mov_poster,all_mov_link)))
        

@mrs.route('/about')
def about():
    return render_template('about.html',mov=movies,l=l,fetch_id=fetch_id,recc=list(zip(a,poster,homepage)),excel_mov=list(zip(excel_mov_name,excel_mov_poster,excel_mov_link))
        ,all_mov_list=list(zip(all_mov_title,all_mov_poster,all_mov_link)))
        


#   history or user code


@mrs.route('/history',methods=["POST","GET"])
def history():
    hist_name.clear()
    hist_id.clear()
    hist_poster.clear()
    con=sqlite3.connect('MRS.db')
    c=con.cursor()
    if(request.method=='POST' or session['uname']!=None):
        c.execute(f"select key from history where uname='{session['uname']}' ")
        rows = c.fetchall()
        for i in rows:
            hist_mov(i[0])
        con.commit()
        con.close()  
        for i in hist_id:
            response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=94477f90c8a637166a3eeff4a7712b96&language=en-US'.format(i))
            data=response.json()
            hist_poster.append("https://image.tmdb.org/t/p/w500/"+data['poster_path'])
            hist_link.append(data['homepage'])
        print(hist_id)
        print(hist_link)
        print(hist_poster)
        return render_template('history.html',mov=movies,l=l,fetch_id=fetch_id,recc=list(zip(a,poster,homepage)),hist=list(zip(hist_name,hist_poster,hist_link))
        ,all_mov_list=list(zip(all_mov_title,all_mov_poster,all_mov_link)))
    else:
        return render_template('history.html',mov=movies,l=l,fetch_id=fetch_id,recc=list(zip(a,poster,homepage)),hist=list(zip(hist_name,hist_poster,hist_link))
        ,all_mov_list=list(zip(all_mov_title,all_mov_poster,all_mov_link)))



#   all movies render code

@mrs.route('/all',methods=["POST","GET"])
def all():
    return render_template('all.html',mov=movies,l=l,all_mov_list=list(zip(all_mov_title,all_mov_poster,all_mov_link)))

#   main file render code

@mrs.route('/home',methods=["POST","GET"])
def recommeded():
    a.clear() 
    fetch_id.clear()
    poster.clear()
    homepage.clear()
    excel_mov_name.clear()
    excel_mov_id.clear()
    excel_mov_poster.clear()

    rec=request.args.get("recommend")
    if rec is not None:    
        recommend(rec)
        exact_mov(rec)
        con=sqlite3.connect('MRS.db')
        c=con.cursor()
        if(session["uname"]):
            c.execute("INSERT INTO history (uname,key) VALUES(?,?)",(session['uname'],rec))
            con.commit()
            con.close()  
        for i in fetch_id:
            response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=94477f90c8a637166a3eeff4a7712b96&language=en-US'.format(i))
            data=response.json()
            poster.append("https://image.tmdb.org/t/p/w500/"+data['poster_path'])
            homepage.append(data['homepage'])
            overview.append(data['overview'])
            vote_avg.append(data['vote_average'])
            release_date.append(data['release_date'])
        for i in excel_mov_id:
            response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=94477f90c8a637166a3eeff4a7712b96&language=en-US'.format(i))
            data=response.json()
            excel_mov_poster.append("https://image.tmdb.org/t/p/w500/"+data['poster_path']) 
            excel_mov_link.append(data['homepage'])
            excel_mov_over.append(data['overview'])
            excel_mov_vote_avg.append(data['vote_average'])
            excel_mov_release_date.append(data['release_date'])
    return render_template('recommeded.html',mov=movies,l=l,fetch_id=fetch_id,recc=list(zip(a,poster,homepage,overview,vote_avg,release_date)),excel_mov=list(zip(excel_mov_name,excel_mov_poster,excel_mov_link,excel_mov_over,excel_mov_vote_avg,excel_mov_release_date)))

#   login code

@mrs.route('/login',methods=['POST','GET'])
def login():  
    con=sqlite3.connect('MRS.db')
    c=con.cursor()
    if request.method=='POST':
        if(request.form["uname"]!="" and request.form["psw"]!=""):
            email=request.form["uname"]
            password=request.form["psw"]
            statement=f"SELECT * from register where email='{email}' AND password='{password}';"         
            c.execute(statement)
            
            data=c.fetchone()
            if data:
                session["uname"] =request.form["uname"]                
                c.execute(f"select key from history where uname='{session['uname']}' ")
                rows = c.fetchall()
                for i in rows:
                    recommend(i[0])
                    exact_mov(i[0])
                con.commit()
                con.close()  

                for i in fetch_id:
                    response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=94477f90c8a637166a3eeff4a7712b96&language=en-US'.format(i))
                    data=response.json()
                    poster.append("https://image.tmdb.org/t/p/w500/"+data['poster_path'])
                    homepage.append(data['homepage'])
                for i in excel_mov_id:
                    response=requests.get('https://api.themoviedb.org/3/movie/{}?api_key=94477f90c8a637166a3eeff4a7712b96&language=en-US'.format(i))
                    data=response.json()
                    excel_mov_poster.append("https://image.tmdb.org/t/p/w500/"+data['poster_path'])
                    excel_mov_link.append(data['homepage'])
                return render_template('index.html',mov=movies,l=l,fetch_id=fetch_id,recc=list(zip(a,poster,homepage)),excel_mov=list(zip(excel_mov_name,excel_mov_poster,excel_mov_link))
                ,all_mov_list=list(zip(all_mov_title,all_mov_poster,all_mov_link)))
            else:
                if not data:
                    return render_template("register.html")
    return render_template('login.html')

#   register code

@mrs.route('/register',methods=['POST','GET'])
def register(): 
    con=sqlite3.connect('MRS.db')
    c=con.cursor()
    if request.method=='POST':
        if(request.form["uname"]!="" and request.form["psw"]!=""):
            email=request.form["uname"]
            password=request.form["psw"]
            statement=f"SELECT * from register where email='{email}' AND password='{password}';"         
            c.execute(statement)
            data=c.fetchone()
            if data:
                return render_template("error.html")
            else:
                if not data:
                    c.execute("INSERT INTO register(email,password) VALUES(?,?)",(email,password))
                    con.commit()
                    con.close()  
                    return render_template("login.html")
    return render_template("register.html")

#   logout from the session code

@mrs.route("/logout")
def logout():
    session["uname"] = None
    return redirect("/")

#   main fxn code

if __name__=='__main__':
    mrs.run(debug=True)