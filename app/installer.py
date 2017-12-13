import os
from subprocess import Popen, PIPE
from multiprocessing import Process, Queue


def run_command(cmd_string, queue):
    proc = Popen('echo ' + cmd_string, shell=True, stdout=PIPE, stderr=PIPE)
    proc.wait()
    queue.put(proc.communicate())


def install_package(software_dict, queue, folder='/opt'):
    interface_commands = {
        'I2C': 'raspi-config nonint do_i2c 0',
        'SPI': 'raspi-config nonint do_spi 0',
    }
    # 1. Install packages
    if software_dict['package_dependencies']:
        packages_str = 'apt-get install -y ' + ' '.join(software_dict['package_dependencies'])
        run_command(packages_str, queue)
    # 2. Enable interfaces (I2C, SPI)
    for interface in software_dict['interfaces']:
        run_command(interface_commands.get(interface), queue)
    # 3. Git clone to /opt/<name>
    destination = os.path.join(folder, software_dict['name'])
    clone_cmd = "git clone --depth=1 {github_link}.git {destination}".format(
        github_link=software_dict['github_link'], destination=destination.lower())
    run_command(clone_cmd, queue)
    # 4. Run post-install commands
    for command in software_dict['post_install']:
        run_command(command, queue)


if __name__ == '__main__':
    queue = Queue()
    p = Process(target=run_command, args=["echo error 1>&2 && echo 1111111111", queue])
    p.start()
    p.join()

    print(queue.get())
