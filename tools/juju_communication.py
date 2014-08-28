from jujuclient import Environment, EnvError
from errors.custom_exceptions import JujuError
import socket
import errno
import logging


class JujuCommunication:
    """
    Manage the communication with the Juju controller
    """

    def __init__(self, creds):
        """
        Constructor, initializes the connection to the Juju Controller
        :param creds: information to get a connection to the Juju Controller
        :exception JujuError: raised if connection to Juju can't be done
        """

        self.logger = logging.getLogger(__name__)
        self._creds = creds
        self.client = None

    def connect(self):
        self.logger.info("Connection with the JUJU Controller")
        self.logger.debug("Server (%s:%s)", self._creds['address'], self._creds['port'])
        self.logger.debug("Token (%s)", self._creds['address'])

        if not self.client:
            try:
                try:
                    self.client = Environment("wss://{}:{}".format(self._creds['address'], self._creds['port']))
                except socket.error as err:
                        if not err.errno in (errno.ETIMEDOUT, errno.ECONNREFUSED, errno.ECONNRESET):
                            raise JujuError("Cannot reach endpoint provided (%s:%s)"
                                            % (self._creds['address'], self._creds['port']), err.message)

                self.client.login(self._creds['token'])
            except EnvError, e:
                raise JujuError("Communication with Juju can't be performed", e.message)

            self.logger.info("Connection successfully established")

    def close(self):
        if self.client:
            self.logger.debug("Closing the communication with Juju")
            self.client.close()
            self.client = None

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
        return self.client.deploy(service_name, charm_name, num_units=num_units)

    def addrelation(self, service_1, service_2):
        """
        Create a relation between two services
        :param service_1: first service for the relation
        :param service_2: second service for the relation
        :return:
        """
        self.logger.info("Adding relation between (%s) and (%s)", service_1, service_2)
        return self.client.add_relation(service_1, service_2)

    def expose(self, service_name):
        """
        Expose a service
        :param service_name: name of the service to expose
        :return:
        """
        self.logger.info("Service (%s) is being exposed", service_name)
        return self.client.expose(service_name)

    def destroyservice(self, service_name):
        """
        Destroy a given service
        :param service_name: name of the service
        :return:
        """
        self.logger.info("Destroying the service (%s)", service_name)
        return self.client.destroy_service(service_name)

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
        return self.client.destroy_machines(machine_numbers, force=True)

    def status(self):
        """
        Get the status of Juju
        :return: status of Juju as a JSON file
        """
        self.logger.info("Get the status of the system")
        return self.client.status()

    def getserviceconfiguration(self, service_name):
        return self.client.get_service(service_name)

    def info(self):
        return self.client.info()


if __name__ == '__main__':
    address = "10.0.3.1"
    port = 17070
    token = "d36784462a74d471e34176613652cb15"

    print "env login"
    environment = Environment("wss://" + address + ":" + str(port))
    environment.login(token)
    print "env logged"

    # print environment.add_local_charm("/home/ubuntu/charms/trusty/torquepbs2.zip", "trusty")
    print environment.deploy("apache2", "local:trusty/torquepbs-1")