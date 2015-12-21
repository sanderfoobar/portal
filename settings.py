import os

# Database connection URI, PostgreSQL or MySQL is suggested.
# Examples, see documentation for more:
# postgresql://foo:bar@localhost:5432/portal
# mysql://foo:bar@localhost/portal
SQLALCHEMY_DATABASE_URI = "postgresql://cuckoo:cuckoo@localhost/portal"

# Secret key used by Flask to generate sessions etc. (This feature is not
# actually used at the moment as we have no user accounts etc).
SECRET_KEY = os.urandom(32)

# IP address of the Cuckoo API.
CUCKOO_API = "127.0.0.1:8090"
