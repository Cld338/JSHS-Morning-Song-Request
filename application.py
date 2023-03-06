from flask import Flask, render_template, request, redirect
from private_tool import *
from models import db
from models import Fcuser
from flask import session 
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm
from datetime import datetime
app = Flask(__name__)

@app.route('/logout',methods=['GET'])
def logout():
    session.pop('userid',None)
    return redirect('/')

@app.route('/login', methods=['GET','POST'])  
def login():  
    form = LoginForm() #로그인 폼 생성
    if form.validate_on_submit(): #유효성 검사
        session['userid'] = form.data.get('userid') #form에서 가져온 userid를 session에 저장
        return redirect('/') #로그인에 성공하면 홈화면으로 redirect    
    return render_template('login.html', form=form)




def add_account(fcuser, id, username, password):
    fcuser.userid = id
    fcuser.username = username
    fcuser.password = password
    db.session.add(fcuser)  # id, name 변수에 넣은 회원정보 DB에 저장
    db.session.commit()  #커밋



def update_accounts(fcuser):
    account=("id", "", "pw")
    add_account(fcuser, *account)

def search_id(input_id):
    ids = []
    data = loadJson(f"{currDir}/static/json/studentID.json")
    for id in data:
        n = id.find(input_id)
        if n+1:
            ids.append((id, n))
    ids = sorted(ids, key=lambda x:(x[1], x[0]))
    print(ids)
    return ids

@app.route("/", methods=["GET", "POST"])
def main():
    print(request.form.keys())    
    print(loadJson(f"{currDir}/static/json/past_queue.json"))
    if "userid" in session.keys():
        id = session["userid"]
    else:
        id=""
    if request.method=="POST":
        queue = loadJson(f"{currDir}/static/json/queue.json")
        if "input-id" in request.form.keys():
            ids = search_id(request.form["input-id"])
            return render_template("index.html", ids=ids, queue=queue, id=id)
        elif "music-check-btn" in request.form.keys():
            past_queue = loadJson(f"{currDir}/static/json/past_queue.json")
            data = queue.pop(int(request.form["music-check-btn"])-1)
            data["date"] = datetime.today().strftime("%Y-%m-%d")
            print(data)
            past_queue.append(data)
            saveJson(f"{currDir}/static/json/queue.json", queue)
            saveJson(f"{currDir}/static/json/past_queue.json", past_queue)
            return render_template("index.html", queue=queue, id=id)
        selectedID = request.form["hidden-id"]
        queue = loadJson(f"{currDir}/static/json/queue.json")
        title = request.form["input-title"].strip()
        singer = request.form["input-singer"].strip()
        url = request.form["input-url"].strip()
        if not(selectedID):
            return render_template("index.html", id=id, queue=queue, error_id_input="신청자를 입력해주세요.")
        elif not(title):
            return render_template("index.html", id=id, queue=queue, error_title_input="노래 제목 입력해주세요.")
        elif not(singer):
            return render_template("index.html", id=id, queue=queue, error_singer_input="가수를 입력해주세요.")
        elif not(url):
             return render_template("index.html", id=id, queue=queue, error_url_input="유튜브 링크를 입력해주세요.")
        data = {
            "id":selectedID,
            "title":title,
            "singer":singer,
            "url":url
        }
        if data not in queue:
            queue.append(data)
        saveJson(f"{currDir}/static/json/queue.json", queue)

    queue = loadJson(f"{currDir}/static/json/queue.json")
    
    return render_template("index.html", queue=queue, id=id)
 
@app.route("/past", methods=["GET", "POST"])
def past_page():
    if "userid" in session.keys():
        id = session["userid"]
    else:
        id=""
    past_queue = loadJson(f"{currDir}/static/json/past_queue.json")
    if request.method=="POST":
        music_title = request.form["search-music"]
        search_queue = []
        for q in past_queue:
            if music_title in q["title"]:
                search_queue.append((q, q["title"].index(music_title)))
        search_queue = [i[0] for i in search_queue]
        return render_template("past_queue.html", queue=search_queue[::-1], id=id, input_text=music_title)
    return render_template("past_queue.html", queue=past_queue[::-1], id=id)
    
    
    
if __name__ == "__main__":
    dbfile = os.path.join(currDir, 'db.sqlite')#db파일을 절대경로로 생성
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile #sqlite를 사용함. (만약 mysql을 사용한다면, id password 등... 더 필요한게많다.)
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  #사용자 요청의 끝마다 커밋(데이터베이스에 저장,수정,삭제등의 동작을 쌓아놨던 것들의 실행명령)을 한다.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False #수정사항에 대한 track을 하지 않는다. True로 한다면 warning 메시지유발
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'
    app.config["WTF_CSRF_ENABLED"] = False
    csrf = CSRFProtect()
    csrf.init_app(app)
    db.init_app(app)
    db.app = app
    # with app.app_context():
        # db.create_all()  #db 생성
    # fcuser=Fcuser()
    # update_accounts(fcuser)
    
    app.run(host='0.0.0.0', port=80, debug=True)