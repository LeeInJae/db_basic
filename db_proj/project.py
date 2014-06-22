# -*- coding: utf-8 -*-
from flask import Flask, jsonify, abort, request, escape, make_response, url_for, render_template,session
import MySQLdb

app = Flask(__name__);

#db=MySQLdb.connect(host="10.73.45.57",user="root",passwd="cowspirit",db="cow")
db=MySQLdb.connect(host = "127.0.0.1",user="cowspirit",passwd="super123",db="toto")

#시작 페이지
@app.route('/')
def index():
	if 'user_name' in session:
		return render_template('main.html', name = str(session.get('user_name')) )
		#return '%s 이미 로그인이 되어 있습니다' % session.get('user_name')
	return render_template( 'index.html' )

@app.route('/logout')
def logout():
	if 'user_name' in session:
		session.pop('user_name', None)
	return render_template('logout.html')
	#return '로그아웃 하셨습니다'
#회원가입 창으로 가기
@app.route('/join')
def input():
	return render_template('join.html')

#로그인 창으로 가기
@app.route('/login')
def login():
	if 'user_name' in session:
		return ' 이미 로그인이 되어 있습니다'
	return render_template('login.html')
	
#튜플 값을 딕셔너리로 만드는 것.
def FetchOneAssoc(cursor) :
    data = cursor.fetchone()
    if data == None :
        return None
    desc = cursor.description

    dict = {}

    for (name, value) in zip(desc, data) :
        dict[name[0]] = value

    return dict

#로그인이 제대로 되었는지 확인
@app.route('/login_success', methods=['GET', 'POST'])
def checklogin():
	if request.method == 'POST':
		cur = db.cursor()
		client_id = request.form['id']
		client_pwd = request.form['pwd']


		arg =(client_id, client_pwd)
		cur.callproc( 'SP_LOGIN', arg)

		res = FetchOneAssoc(cur)
		#return str(res);
		output = ''

		if int(res['chk']) == 1:
			session[ 'user_name' ] = client_id
			return render_template('login_success.html', name = res['user_name'])
		return render_template('login_error.html')# '로그인에 실패'

#회원가입
@app.route('/register', methods=['GET', 'POST'])
def register():
	"""Registers the user."""
	if request.method == 'POST':
		cur = db.cursor()
		client_id = request.form['id']
		client_name = request.form['name']
		clinet_age = request.form['age']	
		client_pwd = request.form['pwd']
		
		arg = (client_id, client_name, clinet_age, client_pwd)
		
		sql ="select count(*) from user";
		cur.execute(sql)
		res1 = cur.fetchone();
		count1 = res1[0]
		
		cur.callproc( 'SP_JOIN',arg)
		
		sql ="select count(*) from user";
		cur.execute(sql)
		res2 = cur.fetchone();
		count2 = res2[0]
		
		if count1 == count2:
			return render_template('join_error.html')
		#sql = "insert into user(Id, Name, Age, Passwd) values( '%s','%s','%s',md5('%s') )" % ( client_id, client_name, int(clinet_age), client_pwd )
		#cur.execute(sql)
		db.commit()
	return render_template('join_success.html')

#update 결과 보여주기
@app.route('/update_bet')
def update_bet():
	return render_template('update_bet.html')

@app.route('/update_bet_user', methods=['GET', 'POST'])
def update_bet_user():
	if request.method == 'POST':
		cur = db.cursor()
		date = request.form['date']
		arg = date
		#return str(date)
		cur.callproc( 'SP_UPDATE',(arg,))
		res = FetchOneAssoc(cur)
		#return str(res['chk_count'])
		#return str(res[0]);
		if str(res['chk_count']) == '0': #해당 날짜는 잘 업데이트
			return render_template('correct_update.html', match_date = date )
		if str(res['chk_count']) == '1': #해당 날짜는 잘 업데이트
			return render_template('already_update.html', match_date = date )
		return render_template('error_update.html')

#자기 정보 보여주기
@app.route('/my_info')
def my_info():
	if 'user_name' in session:
		cur = db.cursor()
		arg =(session['user_name'])
		#return arg[0]

		cur.callproc( 'SP_MY_INFO', (arg,) )

		res = FetchOneAssoc(cur)

		output = ''

		if int(res['chk']) == 1:
			return render_template('my_info.html', name = res['user_name'], age = res['user_age'] ,money = res['user_money'])
		return render_template('my_info_error.html')# '내 정보 보기'

#팀 정보 보여주기
@app.route('/team_info')
def team_info():
	return render_template('team_info.html')

@app.route('/show_team_info', methods=['GET', 'POST'])
def show_team_info():
	if request.method == 'POST':
		cur = db.cursor()
		team_name = request.form['team']
		#return str(team_name)
		sql = "select t.name as team_name, g.name as ground_name, g.location as location from (select * from team where name = '%s') as t inner join homeground as g on t.homeground_number = g.number" % (team_name)
		cur.execute(sql)
		res = cur.fetchone()
		if res is not None:
			return render_template('show_team_info.html', name = res[0], home = res[1] , location = res[2])
		return render_template('team_info_error.html')
	#for row in res:
	#	return str(res)
	#if int(res['chk']) == 1:
	#	return render_template('my_info.html', name = res['user_name'], age = res['user_age'] ,money = res['user_money'])
	#return render_template('my_info_error.html')# '내 정보 보기'


##경기별 추천 팀
@app.route('/recommned_team', methods=['GET', 'POST'])
def recommned_team():
	if request.method == 'POST':
		cur = db.cursor()
		matches_number = request.form['matchnumber']
		arg= matches_number
		cur.callproc('sp_recommend', arg )
		res = FetchOneAssoc(cur)
		return render_template('recommend_team_info.html', name = res['RECOMMEND_TEAM_name'], tot_win = res['tot_win_count'] ,tot_loss = res['tot_loss_count'], win = res['win_count'],loss = res['loss_count'])

#betting 하기 
@app.route('/bet_go', methods=['GET', 'POST'])
def bet_go():
	if request.method == 'POST':
		cur = db.cursor()
		matches_number = request.form['matche_number']
		team_name = request.form['team_name']
		bet_money = request.form['bet_money']
		user_id = session['user_name']
		#return user_id
		#return str(matches_number)
		arg= (matches_number, user_id, team_name, bet_money)

		cur.callproc( 'SP_BET', arg )

		res = FetchOneAssoc(cur)
		#return str( res['avail'])
		if str(res['avail']) == '1': #입력 성공
			return render_template('bet.html', id= user_id, match_number = matches_number ,bet_team_name = team_name, money = bet_money)
		if str(res['avail']) == '2': #이미 배팅을 했다면
			cur=db.cursor()
			sql = "select Money from bet where match_number = '%s' and user_id= '%s'" % (int(matches_number),user_id)
			cur.execute(sql)
			#return str( res['avail'])
			result = cur.fetchall();
			money = int(result[0][0]);
			#return str(money)
			return render_template('bet_already.html', id= user_id, match_number = matches_number ,bet_team_name = team_name, money = money)
		if str(res['avail']) == '3': #잔액이 부족하다면
			return render_template('bet_less.html', id= user_id)	
		#return str(res)
		#return str(arg)
		#cur.callproc('sp_recommend', arg )
		#res = FetchOneAssoc(cur)
	return '2'

#오늘의 경기 보여주기
@app.route('/show_matches')
def show_matches():	
	return render_template('show_matches.html')

@app.route('/show_matches_info', methods=['GET', 'POST'])
def show_matches_info():
	if request.method == 'POST':
		cur = db.cursor()
		matches_date = request.form['date']
		#return str(matches_date)
		sql = "( select M1.number, M1.date,t1.name As Home,t2.name As Away, M1.home_rate, M1.away_rate from (select number, date, Home_Team_Number, Away_Team_Number, home_rate,away_rate from matches where date = '%s') As M1 inner join team as t1 on M1.Home_Team_Number = t1.number inner join team as t2 on M1.Away_Team_Number = t2.number) order by M1.number" % (matches_date)

		cur.execute(sql)
		res = cur.fetchall()
		#return str(res[3][1])
		data_list = []
		
		for row in res:
			#output = output + str(row[2]) + '/'
			output = 'match No.'
			output =  output +  str(row[0]) + " -> date : " + str(row[1]) + " HomeTeam:  " + str(row[2]) + "   VS    AwayTeam:  " + str(row[3]) + "  ( Rate  ->  " +  " Home " + str(row[4]) + ":  Away " + str(row[5]) + " )"
			data_list.append(output)
			#data_info['date'] = str(row[1])
			#data_info['home'] = str(row[2])
			#data_info['away'] = str(row[3])
			#data_list.append(data_info)
		#return jsonify( {'book': data_list})
		return render_template('show_matches_info.html', name= data_list)
		#return jsonify( {'phone book' : data_list})
	#	return render_template('show_team_info.html', name = res[0], home = res[1] , location = res[2])
		#return render_template('team_info_error.html')

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify(  {'error' : 'Not Found'}), 404)

if __name__ == '__main__':
	app.secret_key = "\xa4e\xb6K\xa6\xae$\xaa\x85\x0b\xe1'\xf6D\xff}\x8d\xbd\xfa\xd5\xff$=\xf4"
	app.run(debug = True)