from errors.custom_exceptions import BundleError


class BundleParser:
    """
    Class managing a bundle file, converting it into a dictionary
    """

    config = []

    def __init__(self, bundle):
        """
        Constructor, load the file into a dictionary, a BundleException can be raised if the file is incorrect
        :param bundle: bundle to load
        :exception BundleError: raised if the bundle is incorrect
        """

        if bundle is None or type(bundle) is str:
            raise BundleError("The bundle provided is empty")

        if bundle.values() is None or bundle.values()[0] is None:
            raise BundleError("The bundle provided is incorrectly configured")

        self.config = bundle.values()[0]

    def getservice(self, service_name):
        """
        Get a service data from a specific name
        :param service_name: name of the service to get
        :return: the service data as a dictionary
        """
        if self._serviceexists(service_name):
            return self.config['services'][service_name]
        raise BundleError("Unknown service (%s) requested in the bundle" % service_name)

    def listservices(self):
        """
        List all service names
        :return: services available
        """
        if 'services' in self.config:
            return self.config['services'].keys()
        return []

    def getrelations(self):
        """
        Get all the existing relations of the bundle
        :return: Dictionary containing all the relations of the bundle
        """
        if 'relations' in self.config:
            return self.config['relations']
        return []

    def _serviceexists(self, service_name):
        return 'services' in self.config and service_name in self.config['services']

    def getnumberunits(self, service_name):
        """
        Get the number of units for a given service
        :param service_name: name of the service
        :return: the number of units requires for the service
        """
        if self._serviceexists(service_name) and 'num_units' in self.config['services'][service_name]:
            return self.config['services'][service_name]['num_units']
        raise BundleError("No units provided for the service (%s)", service_name)

    def getcharmname(self, service_name):
        """
        Get the name of the charm associated to the service
        :param service_name: name of the service
        :return: name of the charm associated
        """
        if self._serviceexists(service_name) and 'charm' in self.config['services'][service_name]:
            return self.config['services'][service_name]['charm']
        raise BundleError("No charm provided for the service (%s)", service_name)

    def isexposed(self, service_name):
        """
        Specify if the service needs to be exposed
        :param service_name: name of the service
        :return: True is exposed, False otherwise
        """
        if self._serviceexists(service_name) and 'expose' in self.config['services'][service_name]:
            return bool(self.config['services'][service_name]['expose'])
        return False

    def setservicename(self, old_name, new_name):
        """
        Rename a service with another name
        :param old_name: actual name of the service
        :param new_name: new name of the service
        :return: nothing
        """
        # check if existing
        if not self._serviceexists(old_name):
            raise BundleError("Unknown service (%s) requested in the bundle" % old_name)

        # replace the service key
        self.config['services'][new_name] = self.config['services'].pop(old_name)

        # replace the relation key
        for i, x in enumerate(self.config['relations']):
            for j, y in enumerate(x):
                if ':' in y and y.split(':')[0] == old_name:
                    self.config['relations'][i][j] = ''.join([new_name, ':', str(y.split(':')[1])])
                elif y == old_name:
                    self.config['relations'][i][j] = new_name