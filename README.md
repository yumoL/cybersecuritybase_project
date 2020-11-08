# cybersecuritybase_project

A course project with several [cyber security flaws](https://owasp.org/www-project-top-ten/). This web application is a simple mailbox that allows a user to send messages to another. 

### Installation guides
Run `python3 -m pip install django selenium beautifulsoup4 requests `.

### How to start
- Run `python 3 manage.py migrate` to create a database named db.sqlite3.
- Run `python 3 manage.py runserver` to start the app in http://127.0.0.1:8000/.
- Click the "register" link, go to the registration page and create two accounts. (Two accounts are needed because you need to login using one account and send messages to another.)

**Flaw 1: SQL Injection**

Description: The application uses a SQL query `INSERT INTO mailbox_message (source_id, target_id, time, content) VALUES (“%s”, “%s”, “%s”, “%s”) % (source_id, target_id, datetime.now(), content)` to add a new message to the database. Since the query uses string formatting with the % operator, SQL queries included in the content will be executed, which can cause SQL injection. 

Reproduction: Log in and go to the /sendmail page, send `'content");delete from auth_user; --]` as the message. Consequently, the query that will be executed is `INSERT INTO mailbox_message (source_id, target_id, time, content) VALUES (source_id, target_id, datetime.now(), “content”);delete from auth_user; --”)`. This query will delete all users in the database.

How to fix it: Use parameterized queries instead of string formatting. When using a parameterized query, the code that inserts a massage will be `cursor.execute(‘INSERT INTO mailbox_message (source_id, target_id, time, content) VALUES (?,?,?,?)’, (source_id, target_id, datetime.now(), content))`. In this way, the `content");delete from auth_user; --` will be considered as the content of the message instead of an executable query. Additionally, a more efficient way is to eliminate raw queries and use the database-abstraction APIs that Django provides. In the case of creating a new message, `Message.objects.create(...)` can protect the application from SQL injection. 

**Flaw 2: Cross-Site Scripting XSS**

Description: The application does not validate or sanitize the content of the message. Consequently, an adversary can easily include some HTML scripts in the message. These scripts will be executed in the receiver’s browser when he retrieves his messages.

Reproduction: Go to the /sendmail page, send a message `<script> window.alert(document.cookie) </script>`. When the receiver goes to the /sendmail page, his cookie will pop up in the browser. This example script is not really harmful, however, a malicious user can use AJAX to send the cookie to his server. 

How to fix it: Do not trust any data that users submitted and use the XSS filtering provided by the template system of Django. In 28. line of mail.html, `{{message.content|safe}}` means the application trusts the message.content is safe, which disables the XSS protection by Django. Removing “|safe” will enable the XSS filtering, which, for example, converts “<” to “&lt” and “>” to “&gt” so the script cannot be executed in the browser. 

**Flaw 3: Broken Authentication**

Description: There is no validator in the registration to validate the security level of a password. Consequently, a user can use a well-known password such as “123” or “abc” for his account.

How to fix it: Use regular expressions to validate a password. For example, there can be a validator to check if a password is longer than a specific minimum length and another validator to check if a password contains both uppercase and lowercase letters as well as special symbols such as #, &, and %. There can also be a validator to check if a password is in the list of well-known passwords. Using validators can force a user to create a more completed password. Another option is generating a random password for users, the Django authentication system also provides a `make_random_password` method (https://docs.djangoproject.com/en/3.1/topics/auth/customizing/#django.contrib.auth.models.BaseUserManager.make_random_password) for the generation of random passwords.  

**Flaw 4: Sensitive data exposure**

Description: Passwords are not encrypted and are saved as plain text in the database. Once an adversary has access to the database or obtains the user list using SQL injection, he can directly obtain all passwords without cracking any encryption algorithm. 

How to fix it: In the registration, encrypt passwords before saving them to the database. The password management of Django provides a “make_password” method (https://docs.djangoproject.com/en/1.8/topics/auth/passwords/#django.contrib.auth.hashers.make_password) for password encryption.

**Flaw 5: Broken Access Control**

Description: Once a user logs in, no matter whether he is a superuser (i.e., an admin) or not, he can go to the admin page (http://127.0.0.1:8000/admin/) and remove a user.

How to fix it: In views.py, implement an authorization method to check if a logged-in user is an admin for the `admin_view` and `remove_user` methods. In the authorization method, fetch the logged in user from the database based on his username `user=User.objects.get(request.user.username)`, and then check if `user.is_superuser` is True. If it is true, the user can access the admin page, otherwise, redirect the user to another page that he has access to, such as the index page. 

**Flaw 6: Insufficient Logging and Monitoring**

Description: The application only simply prints the logs to the console without saving them anywhere. Consequently, if an attack happens, exceptions cannot be detected quickly. 

How to fix it: Python’s built-in logging module can be used to implement system logging. The logs can be redirected to a central, secure logging service so the developers can analyze the logs whenever it is necessary. Sensitive data such as session ids and passwords should be excluded when logging. 

**Flaw 7: Security Misconfiguration**

Description: 1) The application runs in debug mode, which means stack traces will be revealed to the users on the web page if an error happens. 2) The application uses SQLite as its database. Since SQLite is a file-based data management system, anyone who knows the location of the file can see its content. 3) settings.py includes the secret key in plain text.

How to fix it: 1) Disable the debug mode by setting “DEBUG=False” and adding “http://127.0.0.1:8000/” to ALLOWED_HOSTS in settings.py. In this way, an error page such as a 404 or 400 page instead of error traces will be shown to users in the case of errors. 2) Use a separate database server such as MySQL and PostgreSQL instead of SQLite so that a separate account (with password) can be set for database maintenance. In this way, if an adversary does not know the password, he cannot see the content of the database even if he can access the server. 3) Save sensitive variables as environment variables in the production environment. The secret key can be retrieved by `SECRET_KEY = os.environ[‘SECRET_KEY’]`.

