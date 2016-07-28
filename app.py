from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from flask import Flask, url_for, Response, send_from_directory, request
import flask
import werkzeug.exceptions as excep
import libethvault.config
import libethvault.db as data

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(libethvault.config.CONFIG["db_loc"])


db = SQLAlchemy(app)


class Vault(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=True)
    vault_addr = db.Column(db.String(42), unique=True)
    owner = db.Column(db.String(42), unique=True)

    def __init__(self, vault, owner, email=None):
        self.email = email
        self.owner = owner
        self.vault_addr = vault

    def __repr__(self):
        return "<Vault %r>" % self.vault_addr


class BlockUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_block = db.Column(db.Integer, nullable=False)

    def __init__(self, blk):
        self.last_block = blk


@app.route("/register", methods=["POST"])
def api_register():
    if request.method == "POST":
        email = str(request.form.get("email", ''))

        if email == '':
            raise excep.HTTPException("Could not decipher email from request.", 400)

        vault = str(request.form.get("vault", ''))

        if vault == '':
            raise excep.HTTPException("Could not parse vault from request.", 400)

        if not data.exists_vault(vault):
            raise excep.HTTPException("Vault does not exist.", 400)

        data.set_email(vault, email)

        return flask.jsonify(new_email=email, vault=vault)

    else:
        raise excep.HTTPException("Bad method.", 405)


@app.route("/", methods=["GET"])
def api_home():
    return send_from_directory("", "home.html")