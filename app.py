from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from jugaad_data.nse import stock_df
from datetime import timedelta,date
import os
import pandas as pd
import plotly.express as px
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import yfinance as yf


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key

#for displaying username on our welcome page
@app.route('/welcome/<username>')
def welcome(username):
    return render_template('welcome.html', username=username)


# Database Configuration given already in the starter code
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

# Initialize Database within Application Context
with app.app_context():db.create_all()

#directly opening the login page and after succesful login(or register then login) our actual webpages will start to show up.
@app.route('/')
def index(): return render_template('login.html')

def get_stock_value(stock_symbol, filter_type):
    try:
        stock_data = yf.Ticker(stock_symbol + ".NS")
        if filter_type == 'Trailing_P/E':
            filtered_data = stock_data.info.get('trailingPE')
            print("hifilter 1")
        elif filter_type == 'Forward_P/E':
            print("hifilter 2 before")
            filtered_data = stock_data.info.get('forwardPE')
            print("hifilter 2 after")
        elif filter_type == 'Forward_EPs':
            print("hifilter 3 before")
            filtered_data = stock_data.info.get('forwardEps')
            print("hifilter 3 after")
        else:
            print("hifilter 4 before")
            filtered_data = stock_data.info.get('trailingEps')
            print("hifilter 4 after")
        
        if filtered_data is not None:
            return filtered_data
        else:
            return None
    except Exception as e:
        print(f"Error fetching data for {stock_symbol}: {str(e)}")
        return None

@app.route('/Filters', methods=['GET', 'POST'])
def Filters():
    if request.method == 'POST':
        filters = request.form.getlist('filter')
        stocks = request.form.getlist('stock')
        values = request.form.getlist('dynamicInput')
        print(filters)
        print(stocks)
        print(values)
        filtered_stocks = []

        for stock_symbol in stocks:
            stock_values = []
            print("hi103")

            for filter_type, filter_value in zip(filters, values):
                filter_value = float(filter_value)
                stock_value = get_stock_value(stock_symbol, filter_type)
                print(stock_value)

                if stock_value is not None and stock_value > filter_value:
                    stock_values.append({"filter_type": filter_type, "value": stock_value})
                    print(stock_values)

                print("hi108")
            if stock_values:
                filtered_stocks.append({"symbol": stock_symbol, "values": stock_values})
                print(filtered_stocks)

        return render_template('Filters.html', filtered_stocks=filtered_stocks)

    return render_template('Filters.html')


@app.route('/stock_analysis', methods=['GET', 'POST'])
def stock_analysis():

    stocks = ['select','ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJFINSV', 'BAJFINANCE', 'BANKBARODA', 'BERGEPAINT', 
    'BHARTIARTL', 'BPCL', 'CANBK', 'CIPLA', 'COALINDIA', 'CUMMINSIND', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'FEDERALBNK', 'GRASIM', 'HCLTECH', 
    'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDPETRO', 'HINDUNILVR', 'ICICIBANK', 'INDUSINDBK', 'INFY', 'IOC', 'ITC', 'JSWSTEEL', 'KOTAKBANK', 
    'LTIM', 'LT', 'MARUTI', 'NESTLEIND', 'NTPC', 'ONGC', 'PFC', 'PNB', 'SBILIFE', 'SBIN', 'SHREECEM', 'TATACONSUM', 'TATASTEEL', 'TECHM', 'TVSMOTOR', 
    'ULTRACEMCO', 'UPL', 'ZYDUSLIFE']

    analysis_types = ['select', 'Market Price','Value','LTP']
    
    time_scale = ['select','1 Day','1 Week','1 Month','1 Year','3 Years','5 Years']
    
    if request.method == 'POST':
        # getting input of stock,analysis type and timescale from the user

        selected_stock = request.form.get('stock')
        selected_analysis_type = request.form.get('analysis_type')
        selected_time_scale = request.form.get('time')

        #specifying the time scale in terms of number of days corresponding to the time_scale selected by the user
        if selected_time_scale== '1 Day':x=1
        elif selected_time_scale== '1 Week':x=7
        elif selected_time_scale== '1 Month':x=30
        elif selected_time_scale== '1 Year':x=365
        elif selected_time_scale== '3 Years':x=1095
        elif selected_time_scale== '5 Years':x=1825


        #when all the three options are specified we can fetch data from jugaad-data and display the plots 
        #by setting the final date as today and start date according to time scale selected
        if selected_stock != 'select' and selected_analysis_type != 'select' and selected_time_scale != 'select':
            end_date = date.today()
            start_date = end_date - timedelta(x)  

            Details = stock_df(selected_stock, start_date, end_date)
            
            required_columns = ['DATE', 'CLOSE', 'LTP','VALUE']
            Details_required = Details[required_columns]
            Details_required['DATE'] = pd.to_datetime(Details_required['DATE'])

            #sorting the dates so that start_date is in the beginning
            Details_required = Details_required.sort_values(by='DATE')

            # first we are saving the csv files and then we will read the csv files to plot the corresponding graph
            csv_path = "stock.csv"
            Details_required.to_csv(csv_path, index=False)
        
    
            #index tells how the data will be written, when it is false S.no. do not appear but when it is 
            #true an additional column of kind-of-serial-nums is created 
            Details_required.to_csv(csv_path, index=False)


        if csv_path:
                df = pd.read_csv(csv_path)
                
                #setting the analysis type according to the columns of jugaad-data, so that fetching is not faltered               
                if selected_analysis_type == 'Market Price':
                    selected_analysis_type = 'CLOSE'

                elif selected_analysis_type == 'Value':
                    selected_analysis_type = 'VALUE'

                elif selected_analysis_type == 'LTP':
                    selected_analysis_type = 'LTP'

                #plotting of the graph
                fig = px.line(Details_required, x='DATE', y=selected_analysis_type, title=f'{selected_stock} Stock Performance')
                fig.update_xaxes(title_text='Date')
                fig.update_yaxes(title_text=selected_analysis_type)
                fig.update_layout(hovermode='x unified')

                #making the plot in dark theme to improve visibility
                fig.update_layout(plot_bgcolor='rgb(0, 0, 0)', paper_bgcolor='rgb(211, 211, 211)')

                #saving the html file in static folder so that we can display it on the webpage
                html_filename = "stock_analysis.html"
                html_path = os.path.join(os.path.dirname(__file__), 'static', html_filename)
                fig.write_html(html_path)
            

                return render_template('stock_analysis.html', stocks=stocks, analysis_types=analysis_types,time_scale=time_scale, plot_html_path=html_path,html_filename=html_filename)

    return render_template('stock_analysis.html', stocks=stocks, analysis_types=analysis_types, time_scale=time_scale)

@app.route('/multiple_stocks', methods=['GET', 'POST'])
def multiple_stocks():
    stocks = ['ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'ASIANPAINT', 'AXISBANK', 'BAJAJFINSV', 'BAJFINANCE', 'BANKBARODA', 'BERGEPAINT',
        'BHARTIARTL', 'BPCL', 'CANBK', 'CIPLA', 'COALINDIA', 'CUMMINSIND', 'DIVISLAB', 'DRREDDY', 'EICHERMOT', 'FEDERALBNK',
        'GRASIM', 'HCLTECH', 'HDFCLIFE', 'HEROMOTOCO', 'HINDALCO', 'HINDPETRO', 'HINDUNILVR', 'ICICIBANK', 'INDUSINDBK', 'INFY',
        'IOC', 'ITC', 'JSWSTEEL', 'KOTAKBANK', 'LTIM', 'LT', 'MARUTI', 'NESTLEIND', 'NTPC', 'ONGC', 'PFC', 'PNB', 'SBILIFE',
        'SBIN', 'SHREECEM', 'TATACONSUM', 'TATASTEEL', 'TECHM', 'TVSMOTOR', 'ULTRACEMCO', 'UPL', 'ZYDUSLIFE'
    ]

    analysis_types = ['select', 'Market Price', 'Value', 'LTP']

    # Get a list of selected stocks from checkboxes and criteria from the dropdown 
    if request.method == 'POST':
        selected_stocks = request.form.getlist('stocks')  
        selected_analysis_type = request.form.get('analysis_type')

        if selected_analysis_type == 'Market Price':
            selected_analysis_type = 'CLOSE'

        elif selected_analysis_type == 'Value':
            selected_analysis_type = 'VALUE'

        elif selected_analysis_type == 'LTP':
            selected_analysis_type = 'LTP'

        if selected_stocks and selected_analysis_type != 'select':
            
            #we are fixing the timescale for this part because if someone wants to compare the stocks he/she would be
            #checking for very latest trends
            x=180

            for stock_symbol in selected_stocks:
                # Fetch historical data using jugaad-data
                end_date = date.today()
                start_date = end_date - timedelta(x)

                Details = stock_df(stock_symbol, start_date, end_date)

                required_columns = ['DATE', 'CLOSE', 'LTP', 'VALUE']
                Details_required = Details[required_columns]
                Details_required['DATE'] = pd.to_datetime(Details_required['DATE'])

                # Sort the DataFrame based on the 'DATE' column
                Details_required = Details_required.sort_values(by='DATE')

                # Save the sorted DataFrame to CSV
                csv_path = f"{stock_symbol}.csv"
                Details_required.to_csv(csv_path, index=False)

            combined_data = pd.DataFrame()

            for stock_symbol in selected_stocks:
                try:
                    stock_data = pd.read_csv(f"{stock_symbol}.csv")
                    
                    stock_data['DATE'] = pd.to_datetime(stock_data['DATE'])
                    stock_data = stock_data.set_index('DATE')
                    combined_data[stock_symbol] = stock_data[selected_analysis_type]

                except Exception as error:
                    print(f"Error reading CSV")

            combined_data = combined_data.reset_index()

            # Generate a line plot using Plotly 
            fig = px.line(combined_data, x='DATE', y=combined_data.columns, title='Multiple Stocks Analysis')
            fig.update_xaxes(title_text='Date')
            fig.update_yaxes(title_text=selected_analysis_type)
            fig.update_layout(hovermode='x unified')  

            # dark mode
            fig.update_layout(plot_bgcolor='rgb(0, 0, 0)', paper_bgcolor='rgb(211, 211, 211)')


            html_filename = "multiple.html"
            html_path = os.path.join(os.path.dirname(__file__), 'static', html_filename)
            fig.write_html(html_path)

            return render_template('multiple_stocks.html', stocks=stocks, analysis_types=analysis_types,plot_html_path=html_path,
                                    html_filename=html_filename)

    return render_template('multiple_stocks.html', stocks=stocks, analysis_types=analysis_types)


#given in starter code
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        new_user = User(username=username, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! Please login.')
        return redirect(url_for('index'))

    return render_template('register.html')

#given in starter code
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()

    if user and check_password_hash(user.password_hash, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))

#given in starter code
@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('welcome.html', username=session['username'])
    else:
        return redirect(url_for('index'))

#given in starter code
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)