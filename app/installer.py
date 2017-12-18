import os
import logging
import shutil
from subprocess import Popen, PIPE
from multiprocessing import Process, Queue

logging.basicConfig(filename='makerhub.log', level=logging.DEBUG,
                    format='%(asctime)-15s %(clientip)s %(user)-8s %(message)s')


class InstallerException(Exception):
    returncode = None
    stdout = None
    stderr = None


def run_command(cmd_string, queue, cwd=None):
    proc = Popen(cmd_string, cwd=cwd, shell=True, stdout=PIPE, stderr=PIPE)
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


if __name__ == '__main__':
    queue = Queue()
    p = Process(target=run_command, args=["echo error 1>&2 && echo 1111111111", queue])
    p.start()
    p.join()
    logging.info("SUCCESS")

    print(queue.get())
