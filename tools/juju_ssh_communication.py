__author__ = 'benoit'
import paramiko
import ntpath


class JujuSSHClient():

    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password

        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _connect(self):
        self.client.connect(self.hostname, port=self.port, username=self.username, password=self.password)

    def _close(self):
        self.client.close()

    def deploylocalcharm(self, service_name, charm_directory):
        self._connect()
        stdin, stdout, stderr = self.client.exec_command("juju deploy --repository=./charms %s %s"
                                                         % (charm_directory, service_name))
        self._close()
        return stdout.readlines(), stderr.readlines()

    def copyfile(self, localfile, unit_name):
        # copy file on the juju controller
        filename = _extractfilename(localfile)
        self._copyfile_tojuju(localfile, filename)
        # copy file from the juju controller on the service desired
        self._copyfile_toservice(filename, unit_name)
        # delete file from juju controller
        self._deletefile(filename)

    def _deletefile(self, file_name):
        self._connect()
        ftp = self.client.open_sftp()
        ftp.remove(file_name)
        ftp.close()
        self._close()

    def _copyfile_tojuju(self, localfile, remotefile):
        self._connect()
        ftp = self.client.open_sftp()
        ftp.put(localfile, remotefile)
        ftp.close()
        self._close()

    def _copyfile_toservice(self, file_location, service_name):
        self._connect()
        stdin, stdout, stderr = self.client.exec_command("juju scp %s %s:" % (file_location, service_name))

        error = stderr.readlines()
        if error:
            raise SystemError(error)
        self._close()

    def runcmd(self, service_name, executable, parameters):
        self._connect()
        stdin, stdout, stderr = self.client.exec_command('juju run --service=%s "bash $HOME/%s %s"'
                                                         % (service_name, executable, ' '.join(parameters)))
        print 'juju run --service=%s "bash $HOME/%s %s"' % (service_name, executable, ' '.join(parameters))
        self._close()
        return stdout.readlines(), stderr.readlines()


def _extractfilename(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
