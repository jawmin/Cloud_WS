from jujuclient import Environment, EnvError
from errors.custom_exceptions import JujuError
import logging

#env.deploy("test-blog", "cs:precise/wordpress-24")
#env.deploy("test-db", "cs:precise/mysql-46")
#env.add_relation("test-db", "test-blog")


class JujuCommunication:
    """
    Manage the communication with the Juju controller
    """

    def __init__(self, address, admin_token, port=17070):
        """
        Constructor, initializes the connection to the Juju Controller
        :param address: address of the juju controller
        :param admin_token: token to access the Juju controller
        :param port: port to reach the Juju API, default 17070
        :exception JujuError: raised if connection to Juju can't be done
        """

        self.logger = logging.getLogger(__name__)
        self.logger.info("Connection with the JUJU Controller")
        self.logger.debug("Server (" + address + ":" + str(port) + ")")
        self.logger.debug("Token (" + admin_token + ")")

        try:
            self._environment = Environment("wss://" + address + ":" + str(port))
            self._environment.login(admin_token)
        except EnvError, e:
            raise JujuError("Communication with Juju can't be performed", e.message)

        self.logger.info("Connection successfully established")

    def deployservice(self, service_name, charm_name, num_units=1):
        """
        Deploy a service on Juju
        :param service_name: name of the service
        :param charm_name: charm to use for the service
        :param num_units: number of units to deploy (min 1)
        :return: None
        """
        self.logger.info("Deploying the service (%s) from the charm (%s) with (%s) unit(s)",
                         service_name, charm_name, num_units)
        return self._environment.deploy(service_name, charm_name, num_units=num_units)

    def addrelation(self, service_1, service_2):
        """
        Create a relation between two services
        :param service_1: first service for the relation
        :param service_2: second service for the relation
        :return:
        """
        self.logger.info("Adding relation between (%s) and (%s)", service_1, service_2)
        return self._environment.add_relation(service_1, service_2)

    def expose(self, service_name):
        """
        Expose a service
        :param service_name: name of the service to expose
        :return:
        """
        self.logger.info("Service (%s) is being exposed", service_name)
        return self._environment.expose(service_name)

    def destroyservice(self, service_name):
        """
        Destroy a given service
        :param service_name: name of the service
        :return:
        """
        self.logger.info("Destroying the service (%s)", service_name)
        return self._environment.destroy_service(service_name)

    def getmachinesforservice(self, service_name):
        """
        Get the list of machines associated to the service and its units
        :param service_name: name of the service
        :return: list of machines
        """
        self.logger.info("Get the list of machine for the service (%s)", service_name)
        status = self.status()
        machines_list = []
        for units_value in status['Services'][service_name]['Units'].values():
            machines_list.append(units_value['Machine'])
        return machines_list

    def destroymachines(self, machine_numbers):
        """
        Destroy machines
        :param machine_numbers: list of machines
        :return:
        """
        self.logger.info("Destroying the machine (%s)", machine_numbers)
        return self._environment.destroy_machines(machine_numbers, force=True)

    def status(self):
        """
        Get the status of Juju
        :return: status of Juju as a JSON file
        """
        self.logger.info("Get the status of the system")
        return self._environment.status()

    def getserviceconfiguration(self, service_name):
        return self._environment.get_service(service_name)

    def info(self):
        return self._environment.info()
