from tools.bundle_parser import BundleParser
from errors.custom_exceptions import DatabaseError
from api.models import Bundle, Service
import logging


class Core:
    """
    Core of the service, manages the communication with Juju and all operations to do
    """

    def __init__(self, user_id, juju_communication, dbsession):
        """
        Constructor, initializes the connection with the Juju Controller
        :param user_id: user performing the action
        :param juju_communication: configuration to access the Juju Controller
        """
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Initialization of the Core for user (%s)", user_id)

        self.user_id = str(user_id)
        self.juju_communication = juju_communication
        self.dbsession = dbsession

        self.logger.debug("Core initialized for user (%s)", user_id)

    def deploybundle(self, bundle_data):
        self.logger.debug("Start the bundle deployment")

        bundle_parser = BundleParser(bundle_data)

        # generate a new bundle ID
        # [a-z] user_id timestamp
        import random
        import string
        import time
        bundle_id = ''.join([random.choice(string.ascii_lowercase), self.user_id, str(int(time.time() * 1000))])
        # replace all service names
        for service_name in list(bundle_parser.listservices()):
            service_id = ''.join([bundle_id, service_name])
            bundle_parser.setservicename(service_name, service_id)

        # adding entry to the database for the bundle
        bundle = Bundle(bundle_id, self.user_id, str(bundle_data))
        self.dbsession.add(bundle)

         # Deploy services
        self.logger.info("Deploying services for the bundle")
        for service_name in bundle_parser.listservices():
            service_charm = bundle_parser.getcharmname(service_name)
            service_units = bundle_parser.getnumberunits(service_name)

            # deploy the service for the given charm
            self.logger.debug("Deploying the service (%s) with the charm (%s) with (%s) unit(s)",
                              service_name, service_charm, service_units)
            self.logger.debug(self.juju_communication.deployservice(service_name, service_charm,
                                                                    num_units=service_units))

            if bundle_parser.isexposed(service_name):
                self.logger.debug("Exposing the service (%s)", service_name)
                self.logger.debug(self.juju_communication.expose(service_name))

            # adding entry to the database for the service
            self.logger.debug("Adding entry to the database")
            service = Service(service_name, bundle_id, service_units)
            self.dbsession.add(service)

        # Create relations
        self.logger.info("Deploying relations for the bundle")
        for relations in bundle_parser.getrelations():
            if len(relations) == 2:
                # add relation
                self.logger.debug("Adding relation between (%s and %s)", relations[0], relations[1])
                self.logger.debug(self.juju_communication.addrelation(relations[0], relations[1]))
            else:
                # skip relation
                self.logger.warn("Incomplete relation detected and won't be added")

        return bundle_id

    def _bundleexists(self, bundle_id):
        bundle = Bundle.by_id(bundle_id)
        if bundle is None:
            self.logger.warn("No bundle named (%s) found in the database", bundle_id)
            raise DatabaseError("No bundle named (%s) found in the database" % bundle_id)
        self.logger.debug("Bundle (%s) found", bundle_id)
        return bundle

    def destroybundle(self, bundle_id):
        self.logger.debug("Start removing the bundle and its services")

        # check if the bundle exists
        bundle = self._bundleexists(bundle_id)

        # check if the user owns the bundle
        if bundle.id_user != self.user_id:
            self.logger.warn("User (%s) is not allowed to delete the bundle (%s)" % (self.user_id, bundle_id))
            raise DatabaseError("User (%s) is not allowed to delete the bundle (%s)" % (self.user_id, bundle_id))

        # delete the services
        for service in bundle.services.all():
            # get the machines list
            machines = self.juju_communication.getmachinesforservice(service.id_service)

            # destroy each service
            self.juju_communication.destroyservice(service.id_service)

            # destroy the machines
            if machines:
                self.juju_communication.destroymachines(machines)

        # delete the bundle from database (with cascade)
        self.logger.debug("User (%s) allowed to delete the bundle (%s)", self.user_id, bundle_id)
        self.dbsession.delete(bundle)

    def statusbundle(self, bundle_id):
        # TODO: change the return for something more detailed if an error is caught
        self.logger.debug("Start getting information about the deployed bundle")

        # check if the bundle exists
        bundle = self._bundleexists(bundle_id)

        # check if the user owns the bundle
        if bundle.id_user != self.user_id:
            self.logger.warn("User (%s) is not allowed to get information about the bundle (%s)"
                             % (self.user_id, bundle_id))
            raise DatabaseError("User (%s) is not allowed to get information about the bundle (%s)"
                                % (self.user_id, bundle_id))

        # get and treat the status
        status = self.juju_communication.status()
        information = []
        started = True
        # print status
        for service in bundle.services.all():
            # pop all services that are not concerned
            # {bundle_name: {service_name: {[unit_name: status],...}, generalStatus: started, pending, error?]},
            # bundle_status: started, pending, error}
            units_list = status['Services'][service.id_service]['Units']
            for unit_name, unit_data in units_list.items():
                state = unit_data['AgentState']
                self.logger.debug('State of (%s) is (%s)', unit_name, state)
                if state != 'started':
                    information.append('{}: {}'.format(unit_name, state))
                    started = False

        result = dict()
        result['Bundle'] = bundle_id
        if started:
            result['Status'] = 'Started'
        else:
            result['Status'] = 'Pending'
            result['Information'] = information

        return result