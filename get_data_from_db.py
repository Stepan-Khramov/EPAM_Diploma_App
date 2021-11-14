#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import mariadb, webbrowser

def main():
    
    db_command = "SELECT * FROM current_year;"
    buffer = []
    result = []
    table_head = "<tr><td>DATE</td><td>COUNTRY</td><td>CONFIRMED</td><td>deaths</td><td>stringency_actual</td><td>stringency</td></tr>"
    #0000:{'date_value': '2021-01-01', 'country_code': 'AFG', 'confirmed': 52513, 'deaths': 2201, 'stringency_actual': 12.04, 'stringency': 12.04, 'stringency_legacy': 20.24, 'stringency_legacy_disp': 20.24}
    html_filename = 'data.html'
   
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
        <div class="nav">
                <p></p>
                <!-- <a href="/index.html">Home
                <p></p>
        <table>'''
    html_ending = '''
        </table>
            </div>
        </body>
        </html>'''

    with open (html_filename, 'w', encoding="utf-8") as html_file:
        html_file.writelines(html_beginning)
        for line in result:
            html_file.writelines('\t\t' + str(line).strip("['']") + '\n')
        html_file.writelines(html_ending)

    #===== Closing connection to SQL DB.
    cursor.close()
    db_conn.close()
    
if __name__ =='__main__':
    main()