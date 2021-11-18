#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import datetime, requests, json, mariadb, os
from flask import Flask


def get_data(date_from, date_to):

    cookies = ''
    status_code = ''
    req_timeout = 5 # Seconds
    login_timeout = 5 # Seconds

    ### Login to phone. Get J100 cookies
    session = requests.Session()

    try:
        # response = session.get('https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/' + date_from + '/' + date_to, verify=False, timeout=login_timeout)
        response = session.get('https://covidtrackerapi.bsg.ox.ac.uk/api/v2/stringency/date-range/' + date_from + '/' + date_to , timeout=req_timeout)
        status_code = response.status_code
        # Retrive session cookies for operations requests
        cookies = session.cookies.get_dict()
        
        resp_data = json.loads(response.text)
        # print(resp_data)
        
    except Exception as exception:
        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S: ") + ' - ' +  str(exception))
    finally:
        ### Close session.
        if session:
            session.close
    return resp_data['data']

def put_data_to_db():

    #===== Getting data from data source.
    source_data = []
    result_data = []

    source_data = get_data('2021-01-01', '2021-01-31')

    for i_source_data_line in list(source_data.keys()):
        for j_source_data_line in list(source_data[i_source_data_line].keys()):
            result_data.append(source_data[i_source_data_line][j_source_data_line])

    # for result_data_line in result_data:
    #     print(result_data_line)

    #===== End of Getting data from data source.

    #===== Connect to SQL DB.
    try:
        db_conn = mariadb.connect(
            # user="stepan",
            # password="stepan",
            # host="192.168.10.66",
            user=os.environ.get('db_user'),
            password=os.environ.get('db_pass'),
            host=os.environ.get('db_host'),
            port=3306,
            database="covid_tracker"

        )
    except mariadb.Error as mariadb_error:
        print("Error connecting to MariaDB: " + str(mariadb_error))
        # sys.exit(1)

    #===== End of Connect to SQL DB.

    #===== Working with SQL DB.
    cursor = db_conn.cursor()
    # print(cursor)
    
    #===== Create table.
    cursor.execute("DROP TABLE IF EXISTS current_year")
    cursor.execute("CREATE TABLE current_year(id INT UNSIGNED AUTO_INCREMENT PRIMARY KEY," "date_value DATE, country_code VARCHAR(3), confirmed INT, deaths INT, stringency_actual FLOAT(5,2), stringency FLOAT(5,2))")
    #0000:{'date_value': '2021-01-01', 'country_code': 'AFG', 'confirmed': 52513, 'deaths': 2201, 'stringency_actual': 12.04, 'stringency': 12.04, 'stringency_legacy': 20.24, 'stringency_legacy_disp': 20.24}


    #insert information 
    for result_data_line in result_data:
        try: 
            cursor.execute("INSERT INTO current_year (date_value, country_code, confirmed, deaths, stringency_actual, stringency) VALUES (?, ?, ?, ?, ?, ?)", (result_data_line['date_value'], result_data_line['country_code'], result_data_line['confirmed'], result_data_line['deaths'], result_data_line['stringency_actual'], result_data_line['stringency']))
        except mariadb.Error as mariadb_error: 
            print("MariaDB error: " + str(mariadb_error))

    db_conn.commit()
    print("Last Inserted ID: " + str(cursor.lastrowid))

    #===== End of Working with SQL DB.

    #===== Closing connection to SQL DB.
    cursor.close()
    db_conn.close()

def put_data_from_db_to_html():
    
    db_command = "SELECT * FROM current_year;"
    buffer = []
    result = []
    table_head = "<tr><td>##</td><td>DATE</td><td>COUNTRY</td><td>CONFIRMED</td><td>deaths</td><td>stringency_actual</td><td>stringency</td></tr>"
    #0000:{'date_value': '2021-01-01', 'country_code': 'AFG', 'confirmed': 52513, 'deaths': 2201, 'stringency_actual': 12.04, 'stringency': 12.04, 'stringency_legacy': 20.24, 'stringency_legacy_disp': 20.24}
    html_filename = 'data.html'
   
    #===== Connect to SQL DB.
    try:
        db_conn = mariadb.connect(
            # user="stepan",
            # password="stepan",
            # host="192.168.10.66",
            user=os.environ.get('db_user'),
            password=os.environ.get('db_pass'),
            host=os.environ.get('db_host'),
            port=3306,
            database="covid_tracker"

        )
    except mariadb.Error as mariadb_error:
        print("Error connecting to MariaDB: " + str(mariadb_error))

    #===== Get data from DB.
    cursor = db_conn.cursor()
    # print(cursor)
    cursor.execute(db_command)
    buffer = cursor.fetchall()

    result.append(table_head)

    for row in buffer:
        a = '<tr><td>' + str(row[0]) + '</td><td>' + str(row[1]) + '</td><td>' + str(row[2]) + '</td><td>' + str(row[3]) + '</td><td>' + str(row[4]) + '</td><td>' + str(row[5]) + '</td></tr>'
        result.append(a)
    
    html_beginning = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        <html>
        <head>
        <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
        <title>Python generated HTML</title>
        </head>
        <body>
        <a href="/index">Home</a>
        <a href="/data">Renew</a>
        <table>'''
    html_ending = '''
        </table>
        </body>
        </html>'''

    # with open (html_filename, 'w', encoding="utf-8") as html_file:
    #     html_file.writelines(html_beginning)
    #     for line in result:
    #         html_file.writelines('\t\t' + str(line).strip("['']") + '\n')
    #     html_file.writelines(html_ending)

    for line in result:
        html_beginning = html_beginning + line
    html_beginning = html_beginning + html_ending

    #===== Closing connection to SQL DB.
    cursor.close()
    db_conn.close()

    return html_beginning


app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
        <html>
        <head>
        <meta content="text/html; charset=ISO-8859-1" http-equiv="content-type">
        <title>Python generated HTML</title>
        </head>
        <body>
        <a href="/data">Display data.
        </body>
        </html>'''

@app.route('/data')
def data():
    put_data_to_db()
    return put_data_from_db_to_html()


if __name__ == '__main__':
    app.run(debug = True, host="0.0.0.0", port=80)
    # app.run()