import os
import logging
import shutil
import platform
import socket
import json
from subprocess import Popen, PIPE
from multiprocessing import Process, Queue


MIN_SPACE = 50 * 2 ** 20  # 50 MB
TEST_REMOTE_SERVER = 'www.google.com'
SUPPORTED_DISTROS = ['raspbian', 'arch', 'debian', 'ubuntu']  # TODO: Create a list of supporred distros
DESTINATION_FOLDER = '/opt'

DATA_FOLDER = '/usr/share/makerhub' if os.path.exists('/usr/share/makerhub') else './data'
IMAGES_FOLDER = os.path.join(DATA_FOLDER, 'images/')
PACKAGES_FILE = os.path.join(DATA_FOLDER, 'packages.json')
DEFAULT_ICON_32_PATH = os.path.join(DATA_FOLDER, 'images/pi-supply-logo-32x32.png')
DEFAULT_ICON_16_PATH = os.path.join(DATA_FOLDER, 'images/pi-supply-logo-16x16.png')
LOG_FILE = os.path.join(os.getcwd(), 'makerhub.log')
logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE)

PYTHON_VERSION = platform.python_version()[0]


class InstallerException(Exception):
    returncode = None
    stdout = None
    stderr = None


def get_software_objects():
    with open(PACKAGES_FILE, 'r') as f:
        content = json.load(f)
    return content["packages"]


def run_command(cmd_string, q, cwd=None):
    logging.debug(cmd_string)
    try:
        proc = Popen(cmd_string.split(' '), cwd=cwd, stdout=PIPE, stderr=PIPE)
        proc.wait()
        if proc.returncode != 0:
            stdout, stderr = proc.communicate()
            raise InstallerException("Non-zero returncode: {}. STDOUT: {}. STDERR:{}. Command: {}".format(
                proc.returncode, stdout, stderr, cmd_string))
    except Exception as exc:
        raise InstallerException(
            "Command \"{}\" failed to run. Output: \"{}\"".format(
                cmd_string, str(exc)))
    else:
        logging.info("Command \"%s\". Return code: %i", cmd_string, proc.returncode)
        result = proc.communicate()
        q.put(result)


def is_apt_available():
    lock_files = ["/var/lib/apt/lists/lock", "/var/lib/dpkg/lock"]
    is_available = True
    for file in lock_files:
        is_available &= os.path.exists(file)
    return is_available


def install_package(software_dict, queue, folder='/opt', callback=None):
    interface_commands = {
        'I2C': 'raspi-config nonint do_i2c 0',
        'SPI': 'raspi-config nonint do_spi 0',
    }
    success = True
    try:
        destination = os.path.join(folder, software_dict['name'])
        logging.info("Installing to %s", (destination))
        if os.path.exists(destination):
            raise InstallerException(
                "Folder \"{}\" exists. Cannot clone git repository.".format(
                    destination))
        # 1. Install packages
        if software_dict['package_dependencies']:
            if not is_apt_available():
                raise InstallerException("APT is being used by another program. Try again later.")
            packages_str = 'apt-get install -y ' + ' '.join(software_dict['package_dependencies'])
            run_command(packages_str, queue)

        # 2. Enable interfaces (I2C, SPI, ...)
        for interface in software_dict['interfaces']:
            run_command(interface_commands.get(interface), queue)

        # 3. Git clone to /opt/<name>
        clone_cmd = "git clone --depth=1 {github_link}.git {destination}".format(
            github_link=software_dict['github_link'], destination=destination.lower())
        run_command(clone_cmd, queue)

        # 4. Run post-install commands
        for step in software_dict['post_install']:
            run_command(step['cmd'], queue, cwd=step.get('cwd'))
    except InstallerException as exc:
        success = False
        # shutil.rmtree(destination, ignore_errors=True)  # Remove git destination folder
        logging.error(str(exc))

    logging.info("Finished installing. Status: " + 'success' if success else 'failure')
    if callable(callback):
        logging.info("Executing callback")
        callback(success)


def check_system():
    # Returns (success: bool, error_message: string)
    success = True
    error_message = None
    # Check distribution
    distribution = platform.linux_distribution()
    if distribution[0].lower() not in SUPPORTED_DISTROS:
        success = False
        error_message = 'Your OS is not supported'
    # Check available space
    statvfs = platform.os.statvfs(DESTINATION_FOLDER)
    if statvfs.f_bfree * statvfs.f_bsize < MIN_SPACE:
        success = False
        error_message = 'Not enough space. Minimum is {} MB'.format(MIN_SPACE / 10 ** 20)
    # Check Internet connection
    try:
        socket.create_connection((socket.gethostbyname(TEST_REMOTE_SERVER), 80), 2)
    except:
        success = False
        error_message = 'No Internet connection'
    return success, error_message


if __name__ == '__main__':
    queue = Queue()
    p = Process(target=run_command, args=["echo error 1>&2 && echo 1111111111", queue])
    p.start()
    p.join()
    logging.info("SUCCESS")

    print(queue.get())
