import os
import logging
import shutil
import platform
import socket
import shlex
from subprocess import Popen, PIPE
from multiprocessing import Process, Queue

logging.basicConfig(filename='installer.log', level=logging.DEBUG)
MIN_SPACE = 50 * 2 ** 20  # 50 MB
TEST_REMOTE_SERVER = 'www.google.com'
SUPPORTED_DISTROS = ['raspbian', 'arch']  # TODO: Create a list of supporred distros
DESTINATION_FOLDER = '/opt'
PACKAGES_FILE = 'resources/packages.json'
DEFAULT_ICON_32_PATH = 'resources/media/pi-supply-logo-32x32.png'
DEFAULT_ICON_16_PATH = 'resources/media/pi-supply-logo-16x16.png'


class InstallerException(Exception):
    returncode = None
    stdout = None
    stderr = None


def run_command(cmd_string, queue, cwd=None):
    proc = Popen(shlex.quote(cmd_string), cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
    proc.wait()
    print("RETURN CODE: " + str(proc.returncode))
    logging.info("Return code: " + str(proc.returncode))
    result = proc.communicate()
    queue.put(result)
    if proc.returncode != 0:
        exc = InstallerException("Command \"{}\" failed. Return code: {}".format(cmd_string, proc.returncode))
        exc.returncode = proc.returncode
        exc.stdout, exc.stderr = result
        raise exc


def install_package(software_dict, queue, folder='/opt', callback=None):
    interface_commands = {
        'I2C': 'raspi-config nonint do_i2c 0',
        'SPI': 'raspi-config nonint do_spi 0',
    }
    destination = os.path.join(folder, software_dict['name'])
    logging.info("Installing to " + destination)
    success = True
    try:
        # 1. Install packages
        if software_dict['package_dependencies']:
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
        for command in software_dict['post_install']:
            run_command(command, queue, cwd=destination)
    except InstallerException as e:
        success = False
        shutil.rmtree(destination, ignore_errors=True)  # Remove git destination folder
        logging.error("Failed command: {}. Return code: {}. stdout: {}. stderr: {}".format(str(e), e.returncode, e.stdout, e.stderr))
        print("Failed: {}".format(str(e)))

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
