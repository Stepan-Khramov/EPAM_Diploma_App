#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import datetime, requests, json, mariadb

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

def main():

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
            user="stepan",
            password="stepan",
            host="192.168.10.66",
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

if __name__ =='__main__':
    main()