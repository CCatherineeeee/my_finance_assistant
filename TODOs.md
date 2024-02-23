- use Blueprint for app creation
- change bank account table's column "user_id" into "user_name"
- user management: https://realpython.com/using-flask-login-for-user-management-with-flask/
- tokenbased authentication (JWT): https://realpython.com/token-based-authentication-with-flask/#objectives
- unit testing?
- model: bank account add new column: when this account is stored; account's bank name, account's name
- compile javascript: https://medium.com/swlh/test-story-635a6c1cfdfd - didn't end up using, 

note:
- to update / delete database: (cd instance; rm database.sqlite; ) rm -rf migrations; mkdir migrations; flask db init -d migrations; flask db migrate; flask db upgrade