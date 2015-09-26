#!/usr/bin/env python2.7
from fabric.api import run, env, task, cd, runs_once, execute, settings, shell_env, put
import json
from pandas.io.json import json_normalize, DataFrame

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
# env.gateway = scw_hosts['scw-gerald']['public_ip']

scw_hosts = {
    'scw-20d11d': {
        'public_ip': '212.47.236.81',
        'private_ip': '10.1.34.140'
    },
    'scw-43ce1e': {
        'public_ip': '212.47.253.52',
        'private_ip': '10.1.16.164'
    },
    'scw-823930': {
        'public_ip': '212.47.233.18',
        'private_ip': '10.1.13.70'
    }
}
# env.gateway = scw_hosts['scw-20d11d']['public_ip']



env.forward_agent = True

env.hosts = [host['public_ip'] for (name, host) in scw_hosts.items()]
# env.hosts = [host['private_ip'] for (name, host) in scw_hosts.items()]
# env.hosts = '212.47.252.133'

env.skip_bad_hosts = True

env.parallel = True

# # env.shell=False
env.shell_escape=False
env.pty=False
env.warn_only=True
env.quiet=True

# DOCKER_HOST=unix:///var/run/weave.sock


def host_type():
    run('uname -s')

def docker_ps():
    run('docker ps')

@task
def docker_pull(image, tag=None):
    with settings(parallel=True, warn_only=True):
        run('docker pull {}'.format(image))
        if tag:
            run('docker tag -f {} {}'.format(image, tag))

    with shell_env(ZMQ_DIR='/home/user/local'):
        pass
# resin/armv7hf-debian:jessie
# resin/armv7hf-buildpack-deps:jessie
# resin/armv7hf-buildpack-deps:jessie-curl
# resin/armv7hf-buildpack-deps:jessie-scm
# docker tag resin/armv7hf-buildpack-deps:jessie-curl buildpack-deps:jessie-curl

@task
def docker_pull_resin_base_images():
    base_images = ["debian:jessie", "buildpack-deps:jessie", "buildpack-deps:jessie-curl", "buildpack-deps:jessie-scm"]
    prefix = "resin/armv7hf-"
    with settings(parallel=True, warn_only=True):
        for image in base_images:
            run('docker pull '+prefix+image)
            run('docker tag '+prefix+image+' '+image)

    base_images = ["alpine:3.2"]
    prefix = "armbuild/"
    with settings(parallel=True, warn_only=True):
        for image in base_images:
            run('docker pull '+prefix+image)
            run('docker tag '+prefix+image+' '+image)



@task
@runs_once
# def docker_build(git_repo, version_dir, tag, prefix=''):
def docker_build(git_repo, target_docker_repo, tag, version, aliases=[]):
    #
    # call docker-container?
    # with temp_dir or dind

    if aliases:
        aliases = aliases.split(";")

    with settings(warn_only=True):
        put('docker_config.json', '.docker/config.json', mode=0600)

        run('mkdir -p /tmp/docker_build || true')
        with cd('/tmp/docker_build'):
            run('git clone '+str(git_repo+' .'))
            with cd(version):
                target = "{0}/{1}:{2}".format(target_docker_repo,tag, version)
                run('docker build -t {0} .'.format(target))
                run('docker push {0}'.format(target))
                for alias in aliases:
                    run('docker tag -f {0} {1}'.format(target, alias))
                # run('docker push {0}/{1}:{2}'.format(target_docker_repo,tag, version))

        run('rm /tmp/docker_build -rf')
        run('rm .docker/config.json')
    # param: git-repo, version-dir
    # git clone
    # provide base-image
    # build new
    # and push



# fab docker_build:"https://github.com/docker-library/java.git","openjdk-8-jre","armhfbuild/java:openjdk-8-jre"
# fab docker_build:"https://github.com/docker-library/java.git","armhfbuild","java","openjdk-8-jre"

# fab docker_build:"https://github.com/docker-library/java.git","armhfbuild","java","openjdk-8-jre","java:8-jre"
# fab docker_build:"https://github.com/docker-library/httpd.git","armhfbuild","httpd","2.4"
# fab docker_build:"https://github.com/armhf-docker-library/docker-node.git","armhfbuild","node","4.1"
# fab docker_build:"https://github.com/armhf-docker-library/golang.git","armhfbuild","golang","1.5"

# fab -H 212.47.253.52 docker_pull:"armhfbuild/java:openjdk-8-jre","java:jre-8"
# fab docker_build:"https://github.com/armhf-docker-library/elasticsearch.git","armhfbuild","elasticsearch","2.0"

## fab docker_build:"https://github.com/nginxinc/docker-nginx.git","armhfbuild","nginx","openjdk-8-jre",["java:8-jre"]
# 212.47.253.52

@task
def docker_script(name, args):
    result = run('docker run {} {}'.format(name, args_bla))
    pass


@task
def weave_report():
    run('weave report')

@task
def docker_containers():
    # needs curl >=7.40 installed
    result = run('curl -sS --unix-socket /var/run/docker.sock http:/containers/json',
        shell=False, shell_escape=False, pty=False, warn_only=True, quiet=True)
    # print json.loads(str(result))
    return json.loads(str(result))

@task
@runs_once
def docker_containers_results():
    results = execute(docker_containers)
    # print(results)
    #
    # return
    #
    # df = DataFrame.from_dict(results.itervalues().next())
    # print(df)

    # print(json_normalize(df, ['state', 'shortname', ['info', 'governor']]))
    # print(json_normalize(df))


    # print json.dumps(results, indent=2)
    result = {}
    for ip, containers in results.items():
        # print("---")
        # print(ip)
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

    with settings(warn_only=True):
        pass
    run('apt-get install -y netcat-openbsd jq')
    run('mkdir /tmp/curl || true')
    with cd('/tmp/curl'):
        run('curl -SOL http://launchpadlibrarian.net/214117046/curl_7.43.0-1ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/214117047/libcurl3-gnutls_7.43.0-1ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/213509493/libnettle6_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/213509493/libnettle6_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/216006031/libgnutls-deb0-28_3.3.15-5ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/213509492/libhogweed4_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/206710934/libtasn1-6_4.5-2_armhf.deb')
        run('dpkg -i *.deb')
        run('apt-get -fy install')
    run('rm /tmp/curl -rf')

    # run('curl -SL git.io/weave -o /usr/local/bin/weave')
    run('curl -SL git.io/rpi_weave -o /usr/local/bin/weave')
    run('chmod a+x /usr/local/bin/weave')
    run('weave setup')
    # consul ?
    # confd ?

@task
def build_elasticsearch():
    # param: git-repo, version-dir
    # git clone
    # provide base-image
    # build new
    # and push
    pass

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
    result = run('uptime',
        shell=False, shell_escape=False, pty=False, quiet=True)
    print(result)
    print(result.command)
    print(result.real_command)
    print(result.failed)
    print(result.succeeded)
    print(result.return_code)

    # return json (or ordered dict)

@task
def start_container():
    pass
    # points to docker-compose.yml on github?
    # where to get the config-data from?
    # consul? confd?

def docker_inspect():
    pass

def start_elasticsearch():
    # git clone https..
    # docker-compse up -d ?
    run('')
    pass
