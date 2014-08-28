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
import os.path

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'database', 'database.db')
app.config.from_object('api.models')
app = init_db(app)


@app.before_first_request
def init():
    db.create_all()

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
        core = Core(user_id, config, db.session)
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
    :param bundle_id: id of the bundle to destroy
    :param user_id: id of the user requesting the deletion
    :return: validation or error message
    """
    try:
        core = Core(user_id, config, db.session)
        core.destroybundle(bundle_id)
        db.session.commit()

        return jsonify({'Bundle deleted': bundle_id})
    except DatabaseError as e:
        db.session.rollback()
        return jsonify({'Message': e.message, 'Error': e.error})


@app.route('/api/v1.0/<int:user_id>/services/<bundle_id>', methods=['GET'])
def status_service(user_id, bundle_id):
    core = Core(user_id, config, db.session)
    data = core.statusbundle(bundle_id)
    return jsonify(data)
    # """
    # Get a deployed service status (service_name-user_id).
    # """
    # try:
    #     service_id = service_name + str(user_id)
    #     juju = JujuCommunication(config['address'], config['token'], port=config['port'])
    #     status = juju.status()
    #
    #     # list of machines for each unit of the service
    #     machines_list = []
    #     for units_value in status['Services'][service_id]['Units'].values():
    #         machines_list.append(units_value['Machine'])
    #
    #     # keep only the concerned service
    #     [status['Services'].pop(i) for i in dict(status['Services']) if i != service_id]
    #     # for service in dict(status['Services']):
    #     #     if service != service_id:
    #     #         status['Services'].pop(service)
    #
    #     # keep only the concerned machines for the service
    #     [status['Machines'].pop(i) for i in dict(status['Machines']) if i not in machines_list]
    #     # for machine in dict(status['Machines']):
    #     #     if machine not in machines_list:
    #     #         status['Machines'].pop(machine)
    #
    #     return jsonify(status)
    # except EnvError as e:
    #     return jsonify({'Error': 'GET: status_service', 'Message': e.error})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'Error': 'Not found', 'Message': error}), 404)


@app.teardown_appcontext
def close_connection(exception):
    db.session.close()


if __name__ == '__main__':
    setup_logging()
    config = readconfig()
#    app.run(host='0.0.0.0')
    app.run(debug=True)
