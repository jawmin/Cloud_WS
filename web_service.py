#!flask/bin/python
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import request
from api.core import Core
from api.models import db, init_db
from errors.custom_exceptions import JujuError
from errors.custom_exceptions import BundleError
from errors.custom_exceptions import DatabaseError
from tools.config_reader import readconfig
from tools.logging_settings import setup_logging
from tools.juju_communication import JujuCommunication
import os.path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'database', 'database.db')
app.config.from_object('api.models')
app = init_db(app)


@app.before_first_request
def init_db():
    db.create_all()


@app.before_request
def init_juju():
    juju_communication.connect()


@app.route('/')
def index():
    print "REST API for Juju"


@app.route('/api/v1.0/<user_id>/services', methods=['POST'])
def deploy_bundle(user_id):
    """
    Deploy a bundle provided as a JSON file for a specific user. The JSON file should be added to the request
    :param user_id: id of the user requesting the deployment
    :return : ID of the created bundle or error message
    """
    bundle = request.json
    try:
        core = Core(user_id, juju_communication, db.session)
        bundle_id = core.deploybundle(bundle)
        db.session.commit()

        return jsonify({'Bundle deployed': bundle_id})
    except (JujuError, BundleError) as e:
        db.session.rollback()
        return jsonify({'Message': e.message, 'Error': e.error})


@app.route('/api/v1.0/<user_id>/services/<bundle_id>', methods=['DELETE'])
def destroy_bundle(user_id, bundle_id):
    """
    Destroy a bundle deployed, services and machines will be deleted
    :param user_id: id of the user requesting the deletion
    :param bundle_id: id of the bundle to destroy
    :return: validation or error message
    """
    try:
        core = Core(user_id, juju_communication, db.session)
        core.destroybundle(bundle_id)
        db.session.commit()

        return jsonify({'Bundle deleted': bundle_id})
    except DatabaseError as e:
        db.session.rollback()
        return jsonify({'Message': e.message, 'Error': e.error})


@app.route('/api/v1.0/<int:user_id>/services/<bundle_id>', methods=['GET'])
def status_service(user_id, bundle_id):
    """
    Get the status of a given bundle being deployed or deployed
    :param user_id: id of the user requesting the information
    :param bundle_id: id of the bundle to get the status
    :return: status or error
    """
    core = Core(user_id, juju_communication, db.session)
    data = core.statusbundle(bundle_id)
    return jsonify(data)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Not found', 'Message': error}), 404)


@app.teardown_appcontext
def close_connection(exception):
    db.session.close()
    juju_communication.close()


if __name__ == '__main__':
    setup_logging()
    juju_communication = JujuCommunication(readconfig())
#    app.run(host='0.0.0.0')
    app.run(debug=True)
