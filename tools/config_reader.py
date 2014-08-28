from ConfigParser import ConfigParser, ParsingError


def __readaddress():
    """
    Read the standard input to get the address of the Juju controller
    :return: the entered value for the address
    """
    return raw_input("What is the juju server address? ")


def __readport():
    """
    Read the standard input to get the port to access Juju API
    :return: the entered value for the port
    """
    return raw_input("What is the juju service port to access the API? ")


def __readtoken():
    """
    Read the standard input to get the token to access Juju
    :return: the entered value for the token
    """
    return raw_input("What is the token to access the API? ")


def __returnjson(address, port, token):
    """
    Get a JSON file for the following parameters
    :param address: address of the Juju controller
    :param port: port to access the Juju API
    :param token: token to access the Juju full functionalities
    :return: JSON file for the parameters
    """
    return {'address': address,
            'port': port,
            'token': token}


def __writeconfig(address, port, token):
    """
    Write a configuration into a file
    :param address: address of the Juju controller
    :param port: port to access the Juju API
    :param token: token to access the Juju full functionalities
    """
    config = ConfigParser()

    config.add_section('JujuServer')
    config.set('JujuServer', 'address', address)
    config.set('JujuServer', 'port', port)
    config.set('JujuServer', 'token', token)

    with open('local.conf', 'w') as configFile:
        config.write(configFile)


def __newconfig():
    """
    Get a new configuration and save it into a file
    :return: JSON containing the new configuration created
    """
    address = __readaddress()
    port = __readport()
    token = __readtoken()

    __writeconfig(address, port, token)
            
    return __returnjson(address, port, token)


def __treatconfig():
    """
    Get the data from an existing configuration file
    :return: JSON containing the configuration file
    """
    try:
        config = ConfigParser()
        config.readfp(open('local.conf'))

        if config.has_section('JujuServer'):
            # Has section, then check each param
            modified = False

            # Test address
            if config.has_option('JujuServer', 'address'):
                address = config.get('JujuServer', 'address')
            else:
                address = __readaddress()
                modified = True

            # Test port
            if config.has_option('JujuServer', 'port'):
                port = config.getint('JujuServer', 'port')
            else:
                port = __readport()
                modified = True

            # Test token
            if config.has_option('JujuServer', 'token'):
                token = config.get('JujuServer', 'token')
            else:
                token = __readtoken()
                modified = True

            # If a modification was needed, then rewrite the configuration into the file
            if modified:
                __writeconfig(address, port, token)

            return __returnjson(address, port, token)
        else:
            # Doesn't have section, create a new configuration
            return __newconfig()
    except ParsingError:
        # Incorrect file detected, create a new configuration
        print "Parsing error"
        return __newconfig()


def readconfig():
    """
    Get the config from the configuration file.
    If the configuration file is not existing, misses data or incorrect, a new configuration will be created.
    :return: JSON containing the config loaded
    """
    import os.path
    if os.path.isfile('local.conf'):
        # return what is existing
        return __treatconfig()
    else:
        # return a new configuration
        return __newconfig()
