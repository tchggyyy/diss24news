from calendar import month
from datetime import date
from flask import Flask, render_template, request
from predict import utils
from predict.model import perform_training
import pandas as pd
import requests
from urllib.parse import unquote,quote
import feedparser
from sqlalchemy import create_engine
import math


app = Flask(__name__)

#連接資料庫
username = 'zuluwin'     # 資料庫帳號
password = '123456789'     # 資料庫密碼
host = '172.22.35.211'    # 資料庫位址
port = '3306'         # 資料庫埠號
database = 'news'   # 資料庫名稱
table = 'news1'   # 表格名稱

# 建立資料庫引擎
engine = create_engine(f'mysql+pymysql://{username}:{password}@{host}:{port}/{database}')
# 建立資料庫連線
connection  = engine.connect()


@app.route('/')
def found():
    title = "即時幣價"
    return render_template('index.html', title=title)
						   
@app.route('/index')
def index():
    title = "即時幣價"
    return render_template('index.html', title=title)


    

@app.route('/news', methods=['GET', 'POST'])
def analytics():
    title = "幣圈新聞"
    num = ['-06-','-07-','-08-','-09-','-10-']
    opt=len(num)  
    if request.method == "GET":
        sql=' SELECT date, label, title, content, url FROM news1 '
        df = pd.read_sql_query(sql, engine, coerce_float=True)
        page = int(request.args.get('page',1) )
        per_page = int(request.args.get('per_page',20))
        total_pages = math.ceil(len(df)/per_page)
        connection.close()
    else:
        num = request.form[ 'send' ]
        sql=f'''  SELECT date, label, title, content, url FROM news1 WHERE date like '%%{num}%%'  '''
        df = pd.read_sql_query(sql, engine, coerce_float=True)
        page = int(request.args.get('page',1) )
        per_page = int(request.args.get('per_page',20))
        total_pages = math.ceil(len(df)/per_page)
        connection.close()
        num = ['-06-','-07-','-08-','-09-','-10-']
    return render_template( 'news.html',title=title,total_pages=total_pages,outputs=df, page=page,num=num,opt=opt )                      


# @app.route('/predict')
# def charts():
#   title = "預測模型"
#   return render_template('predict.html', title=title)

@app.route('/risk')
def risk():
    title = "風險分類"
    return render_template('risk.html', title=title)

@app.route('/team')
def team():
    title = "團隊介紹"
    return render_template('team.html', title=title)

@app.route('/_demo')
def demo():
    title = "測試頁面"
    return render_template('_demo.html', title=title)

all_files = utils.read_all_stock_files('predict/individual_stocks_5yr')



@app.route('/predict')
def landing_function():
    title = "預測模型"
    stock_files = list(all_files.keys())
    stock_files.sort()

    return render_template('predict.html', show_results="false", title=title,
                           stocklen=len(stock_files), stock_files=stock_files, len2=len([]),
                           all_prediction_data=[],
                           prediction_date="", dates=[], all_data=[], len=len([]))


@app.route('/process', methods=['POST'])
def process():
    title="模型預測結果"
    stock_file_name = request.form['stockfile']
    ml_algoritms = request.form.getlist('mlalgos')
    df = all_files[str(stock_file_name)]
    stockname = str(stock_file_name)
    all_prediction_data, all_prediction_data, prediction_date, dates, all_data, all_data, all_test_evaluations = \
        perform_training(str(stock_file_name), df, ml_algoritms)
    stock_files = list(all_files.keys())
    stock_files.sort()

    return render_template('predict.html', all_test_evaluations=all_test_evaluations, show_results="true",title=title,
                           stocklen=len(stock_files), stock_files=stock_files,
                           len2=len(all_prediction_data),
                           all_prediction_data=all_prediction_data,
                           prediction_date=prediction_date, dates=dates, all_data=all_data, len=len(all_data),
                           stockname=stockname)

@app.route('/stockplot')
def stockplot():
    df = pd.read_csv("./data/BTCUSDT.csv")
    df = df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
    r = df.values.tolist()
    return {"res": r}



if __name__=="__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
	
    #app.run(debug=True, port=5001)
