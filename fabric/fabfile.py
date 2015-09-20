#!/usr/bin/env python2.7
from fabric.api import run, env, task, cd, runs_once, execute
import json


scw_hosts = {
    'scw-thomas': {
        'public_ip': '212.47.244.219',
        'private_ip': '10.1.42.244'
    },
    'scw-sascha': {
        'public_ip': '212.47.239.125',
        'private_ip': '10.1.7.2'
    },
    'scw-webwurst': {
        'public_ip': '212.47.252.133',
        'private_ip': '10.1.6.227'
    },
    'scw-gerald': {
        'public_ip': '212.47.252.255',
        'private_ip': '10.1.7.1'
    },
    'scw-jannik': {
        'public_ip': '212.47.252.205',
        'private_ip': '10.1.7.0'
    },
    'scw-mila': {
        'public_ip': '212.47.243.114',
        'private_ip': '10.1.6.248'
    }
}

env.gateway = scw_hosts['scw-webwurst']['public_ip']
env.forward_agent = True

# env.hosts = [host['public_ip'] for (name, host) in scw_hosts.items()]
env.hosts = [host['private_ip'] for (name, host) in scw_hosts.items()]
# env.hosts = '212.47.252.133'

env.parallel = True

def host_type():
    run('uname -s')

def docker_ps():
    run('docker ps')

def weave_report():
    run('weave report')

@task
def docker_containers():
    # run('echo -e "GET /images/json HTTP/1.0\r\n" | nc -U /var/run/docker.sock | jq "."')
    # needs curl >=7.40 installed
    # return run('curl -sS --unix-socket /var/run/docker.sock http:/containers/json | jq -r ".[].Names[]"')
    # result = run('curl -sS --unix-socket /var/run/docker.sock http:/containers/json | jq -r "."', shell=False, shell_escape=False, pty=False)
    result = run('curl -sS --unix-socket /var/run/docker.sock http:/containers/json',
        shell=False, shell_escape=False, pty=False, warn_only=True, quiet=True)
    # return json.dumps(json.loads(str(result)))
    return json.loads(str(result))

@task
@runs_once
def docker_containers_results():
    # print "---"
    results = execute(docker_containers)
    # print results

    # print json.dumps(results, indent=2)
    result = {}
    for ip, containers in results.items():
        # print("---")
        print(ip)
        # print(json.dumps(result, indent=2))
        # for container in containers:
        #     # print(json.dumps(container, indent=2))
        #     print(container['Names'])
        result[ip] = [container['Names'] for container in containers]
        # blub[ip] = result['Names']

    print(json.dumps(result, indent=2))

# def find all weave-nodes
#

# start container on specific host
# provide documentation?
# specify volumes?
# rocker?

@task
def deploy():
    # run('apt-get update')
    run('apt-get install -y netcat-openbsd jq')
    run('mkdir /tmp/curl || true')
    with cd('/tmp/curl'):
        run('curl -SOL http://launchpadlibrarian.net/214117046/curl_7.43.0-1ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/214117047/libcurl3-gnutls_7.43.0-1ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/213509493/libnettle6_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/213509493/libnettle6_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/216006031/libgnutls-deb0-28_3.3.15-5ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/213509492/libhogweed4_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/206710934/libtasn1-6_4.5-2_armhf.deb')
        run('dpkg -i *.deb')
    run('rm /tmp/curl -rf')
    # weave
    # curl, jq ?
    # consul ?
    # confd ?

@task
def update_packages():
    # better than this: install new server, remove old one
    run('apt-get update')
    run('apt-get upgrade -y')

@task
def repair_and_clean():
    run('apt-get -f -y install')

@task
def get_load():
    run('uptime')

@task
def start_container():
    pass
    # points to docker-compose.yml on github?
    # where to get the config-data from?
    # consul? confd?
