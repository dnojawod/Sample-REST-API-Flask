from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_mysqldb import MySQL, MySQLdb

application = Flask(__name__)
application.config['MYSQL_HOST'] = 'localhost'
application.config['MYSQL_USER'] = 'root'
application.config['MYSQL_PASSWORD'] = ''
application.config['MYSQL_DB'] = 'api'
application.config['MYSQL_CURSORCLASS'] = 'DictCursor'
api = Api(application)
mysql = MySQL(application)

class Book(Resource):
    def get(self):
        query_parameters = request.args

        id = query_parameters.get('id')
        title = query_parameters.get('title')
        author = query_parameters.get('author')

        query = "SELECT * FROM book WHERE"
        to_filter = []

        if id:
            query += " id=%s AND"
            to_filter.append(id)
        if title:
            query += " title=%s AND"
            to_filter.append(title)
        if author:
            query += " author=%s AND"
            to_filter.append(author)
        if not (id or title or author):
            query = "SELECT * FROM book ???"

        query = query[:-4]

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(query, to_filter)
        results = cursor.fetchall()
        if not results:
            return self.page_not_found(404)
        return jsonify(results)

    def post(self):
        if request.json:
            content = request.json
            for entry in content:
                id = entry.get('id')
                title = entry.get('title')
                author = entry.get('author')
                description = entry.get('description')
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                to_filter = []
                to_filter.append(id)
                result = cursor.execute('SELECT * FROM book WHERE id=%s', to_filter)
                if result:
                    return self.page_not_found(409)
                to_filter.pop()
                to_filter.append(author)
                to_filter.append(title)
                result = cursor.execute('SELECT * FROM book WHERE author=%s AND title=%s', to_filter)
                if result:
                    return self.page_not_found(409)
                cursor.execute('INSERT INTO book (title,author,description,id) VALUES (%s,%s,%s,%s)',
                               (title, author, description, id))
                mysql.connection.commit()
            return "Entry committed"
        else:
            return self.page_not_found(404)

    def put(self):
        if request.json:
            content = request.json
            for entry in content:
                id = entry.get('id')
                title = entry.get('title')
                author = entry.get('author')
                description = entry.get('description')
                query = "UPDATE book SET"
                to_filter = []

                if title:
                    query += " title=%s,"
                    to_filter.append(title)
                if author:
                    query += " author=%s,"
                    to_filter.append(author)
                if description:
                    query += " description=%s,"
                    to_filter.append(description)
                if not id:
                    return self.page_not_found(404)

                to_filter.append(id)
                query = query[:-1] + " WHERE id=%s"

                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                result = cursor.execute(query, to_filter)
                if not result:
                    return self.page_not_found(404)
                mysql.connection.commit()
            return "Entry updated"
        else:
            return self.page_not_found(404)

    def delete(self):
        if request.args:
            query_parameters = request.args

            id = query_parameters.get('id')
            title = query_parameters.get('title')
            author = query_parameters.get('author')

            query = "DELETE FROM book WHERE"
            to_filter = []

            if id:
                query += " id=%s AND"
                to_filter.append(id)
            if title:
                query += " title=%s AND"
                to_filter.append(title)
            if author:
                query += " author=%s AND"
                to_filter.append(author)

            query = query[:-4]

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            result = cursor.execute(query, to_filter)
            if not result:
                return self.page_not_found(404)
            mysql.connection.commit()
            return "Entry deleted"
        else:
            return self.page_not_found(404)

    def page_not_found(self, e):
        if e == 404:
            return "<h1>404</h1><p>The resource could not be found.</p>", 404
        elif e == 409:
            return "<h1>409</h1><p>The resource already existing.</p>", 409

api.add_resource(Book, "/api/v1/resources/books")

if __name__ == '__main__':
    application.run(host='0.0.0.0',debug=True)