#!/usr/bin/env python2.7
from fabric.api import run, env, task, cd, runs_once, execute, settings, shell_env, put, execute, roles
import json, re
# from pandas.io.json import json_normalize, DataFrame

host_ids = {
    'manager1': 'a3ecf088-26f3-406d-90c5-0ca92ee857d5',
    'agent1': 'dd489ebf-6b49-4bd9-b294-5eba1a84e722',
    'agent2': 'c9fe8309-140e-4cb8-aa29-9d3793e2c88b'
}

env.roledefs = {
    'all': ["{}.priv.cloud.scaleway.com".format(host_ids[name]) for name in host_ids],
    'managers': ["{}.priv.cloud.scaleway.com".format(host_ids[name]) for name in host_ids if re.search('^manager\d', name)],
    'agents': ["{}.priv.cloud.scaleway.com".format(host_ids[name]) for name in host_ids if re.search('^agent\d', name)],
}
for name, id in host_ids.items():
    env.roledefs[name] = ["{}.priv.cloud.scaleway.com".format(id)]

env.gateway = "{}.pub.cloud.scaleway.com".format(host_ids['manager1'])
# env.gateway = 'a3ecf088-26f3-406d-90c5-0ca92ee857d5.pub.cloud.scaleway.com'

print(env.gateway)
env.forward_agent = True

print(env.roledefs)

# fab --parallel --hosts 212.47.253.68,212.47.235.218 \
#   docker_build:"https://github.com/docker-library/java.git","armhfbuild","java","openjdk-8-jre","java:8-jre"

env.skip_bad_hosts = True

env.parallel = True

# # env.shell=False
env.shell_escape=False
env.pty=False
env.warn_only=True
env.quiet=True

# DOCKER_HOST=unix:///var/run/weave.sock

# This is the user-facing task invoked on the command line.
@task
def deploy(lookup_param):
    # deploy manager
    # deploy agents

    # This is the magic you don't get with @hosts or @roles.
    # Even lazy-loading roles require you to declare available roles
    # beforehand. Here, the sky is the limit.
    host_list = external_datastore.query(lookup_param)
    # Put this dynamically generated host list together with the work to be
    # done.
    execute(do_work, hosts=host_list)


@task
def host_type():
    run('uname -s')

@task
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
# debian:wheezy FIXME

@task
def docker_pull_base_images():
    base_images = ["debian:jessie", "buildpack-deps:jessie", "buildpack-deps:jessie-curl", "buildpack-deps:jessie-scm"]
    prefix = "resin/armv7hf-"
    with settings(parallel=True, warn_only=True):
        for image in base_images:
            run('docker pull '+prefix+image)
            run('docker tag -f '+prefix+image+' '+image)
    run('docker tag -f debian:jessie debian:latest')

    base_images = ["alpine:3.2"]
    prefix = "armbuild/"
    with settings(parallel=True, warn_only=True):
        for image in base_images:
            run('docker pull '+prefix+image)
            run('docker tag -f '+prefix+image+' '+image)

    base_images = ["ubuntu:14.04"]
    prefix = "armhfbuild/"
    with settings(parallel=True, warn_only=True):
        for image in base_images:
            run('docker pull '+prefix+image)
            run('docker tag -f '+prefix+image+' '+image)
    run('docker tag -f ubuntu:14.04 ubuntu:latest')

    base_images = ["ubuntu:14.04"]
    prefix = "armv7/armhf-"
    with settings(parallel=True, warn_only=True):
        for image in base_images:
            run('docker pull '+prefix+image)
            # run('docker tag -f '+prefix+image+' '+image)

@task
def docker_pull_other_images():
    base_images = ["golang:1.4", "golang:1.5", "swarm"] #..
    prefix = "armhfbuild/"
    with settings(parallel=True, warn_only=True):
        for image in base_images:
            run('docker pull '+prefix+image)
            run('docker tag -f '+prefix+image+' '+image)


@task
@runs_once
# def docker_build(git_repo, version_dir, tag, prefix=''):
def docker_build(git_repo, target_docker_repo, tag, version, aliases=[]):
    # version_in_subdir=True
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
        # run('rm .docker/config.json')
    # param: git-repo, version-dir
    # git clone
    # provide base-image
    # build new
    # and push

@task
def docker_push(image):
    run('docker push {0}'.format(image))

# fab docker_build:"https://github.com/docker-library/java.git","armhfbuild","java","openjdk-8-jre","java:8-jre"
# fab docker_build:"https://github.com/docker-library/httpd.git","armhfbuild","httpd","2.4"
# fab docker_build:"https://github.com/armhf-docker-library/docker-node.git","armhfbuild","node","4.1"
# fab docker_build:"https://github.com/armhf-docker-library/golang.git","armhfbuild","golang","1.5"
# fab docker_build:"https://github.com/armhf-docker-library/golang.git","armhfbuild","golang","1.4"

# fab docker_build:"https://github.com/docker/docker.git","armhfbuild","docker","experimental"


# fab -H 212.47.253.52 docker_pull:"armhfbuild/java:openjdk-8-jre","java:jre-8"
# fab docker_build:"https://github.com/armhf-docker-library/elasticsearch.git","armhfbuild","elasticsearch","2.0"

## fab docker_build:"https://github.com/nginxinc/docker-nginx.git","armhfbuild","nginx","openjdk-8-jre",["java:8-jre"]
# 212.47.253.52

@task
def docker_login():
    put('docker_config.json', '.docker/config.json', mode=0600)

@task
def docker_logout():
    run('rm .docker/config.json')


@task
def build_swarm_image(git_tag="v0.4.0-rc2"):
    with settings(warn_only=True):
        # put('docker_config.json', '.docker/config.json', mode=0600)

        run('mkdir -p /tmp/docker_build || true')
        with cd('/tmp/docker_build'):
            run('git clone https://github.com/armhf-docker-library/swarm-library-image.git .')
            run('docker tag -f debian:jessie debian:latest')
            run('./update.sh {}'.format(git_tag))

            target = "{0}/{1}:{2}".format("armhfbuild","swarm", git_tag)
            run('docker build -t {0} .'.format(target))
            run('docker push {0}'.format(target))
            run('docker tag -f {0} {1}'.format(target, "swarm:{}".format(git_tag)))

        run('rm /tmp/docker_build -rf')


@task
def deploy_docker_swarm():
    with settings(warn_only=True):
        put('etc_default_docker', '/etc/default/docker')


@task
def build_docker_image(git_tag="master", experimental=True):
    # https://github.com/docker/docker/tree/v1.8.2
    with settings(warn_only=True):
        # put('docker_config.json', '.docker/config.json', mode=0600)

        run('mkdir -p /tmp/docker_build || true')
        with cd('/tmp/docker_build'):
            run('git clone -b {} --single-branch https://github.com/docker/docker.git .'.format(git_tag))
            run('curl -SL -o Dockerfile https://raw.githubusercontent.com/umiddelb/armhf/master/Dockerfile.armv7')

            env = "DOCKER_EXPERIMENTAL={}".format("1" if experimental else "0")
            run('make build')
            run('{} make binary'.format(env))

            run('cp bundles /root/bundles --recursive')
            # run('cp bundles/1.9.0-dev/binary/docker ~/docker-1.9.0-dev{}'format('-experimental' if experimental else ''))

            # tag = 'master-experimental' if experimental else 'master'
            # target = "{0}/{1}:{2}".format("armhfbuild","docker", git_tag)
            # run('docker build -t {0} .'.format(target))
            # run('docker push {0}'.format(target))
            # run('docker tag -f {0} {1}'.format(target, "swarm:{}".format(git_tag)))

            # tag='master', experimental=False
            # $ docker tag docker-dev:master armhfbuild/docker-dev:master
            # $ docker push armhfbuild/docker-dev:master


        run('rm /tmp/docker_build -rf')


@task
def build_docker_weave(git_tag="master"):
    print("FIXME does not work")
    return
    # https://github.com/docker/docker/tree/v1.8.2
    with settings(warn_only=True):
        # put('docker_config.json', '.docker/config.json', mode=0600)

        run('mkdir -p /tmp/docker_build || true')
        with cd('/tmp/docker_build'):
            run('git clone -b {} --single-branch https://github.com/weaveworks/weave.git .'.format(git_tag))
            run('docker build -t weaveworks/weave-build build')
            run('docker run -v /var/run/docker.sock:/var/run/docker.sock weaveworks/weave-build https://github.com/weaveworks/weave.git')
            # $ sudo docker run -v /var/run/docker.sock:/var/run/docker.sock weaveworks/weave-build -b <branch name> <repo URI>
            # push

            run('docker tag -f weaveworks/weave armhfbuild/weave')
            run('docker push armhfbuild/weave')
            run('docker tag -f weaveworks/weave armhfbuild/weavedns')
            run('docker push armhfbuild/weavedns')
            run('docker tag -f weaveworks/weave armhfbuild/weaveexec')
            run('docker push armhfbuild/weaveexec')

        run('rm /tmp/docker_build -rf')

@task
def build_docker_plugin_weave(git_tag="master"):
    # https://github.com/docker/docker/tree/v1.8.2
    with settings(warn_only=True):
        # put('docker_config.json', '.docker/config.json', mode=0600)

        run('mkdir -p /tmp/docker_build || true')
        with cd('/tmp/docker_build'):
            run('git clone -b {} --single-branch https://github.com/weaveworks/docker-plugin.git .'.format(git_tag))

            run('curl -SL -o Dockerfile https://raw.githubusercontent.com/umiddelb/armhf/master/Dockerfile.armv7')

            env = "DOCKER_EXPERIMENTAL={}".format("1" if experimental else "0")
            run('make build')
            run('{} make binary'.format(env))

            run('cp bundles /root/bundles --recursive')
            # run('cp bundles/1.9.0-dev/binary/docker ~/docker-1.9.0-dev{}'format('-experimental' if experimental else ''))

            # tag = 'master-experimental' if experimental else 'master'
            # target = "{0}/{1}:{2}".format("armhfbuild","docker", git_tag)
            # run('docker build -t {0} .'.format(target))
            # run('docker push {0}'.format(target))
            # run('docker tag -f {0} {1}'.format(target, "swarm:{}".format(git_tag)))

            # tag='master', experimental=False
            # $ docker tag docker-dev:master armhfbuild/docker-dev:master
            # $ docker push armhfbuild/docker-dev:master


        run('rm /tmp/docker_build -rf')

@task
def build_calico(git_tag="master"):
    with settings(warn_only=True):
        # put('docker_config.json', '.docker/config.json', mode=0600)

        run('mkdir -p /tmp/docker_build || true')
        with cd('/tmp/docker_build'):
            run('git clone -b {} --single-branch https://github.com/projectcalico/calico-docker.git .'.format(git_tag))
            run('make node')
            # calico/node:latest
            run('make binary')

        run('rm /tmp/docker_build -rf')

# fab --roles managers swarm_create

# @runs_once
@roles('managers')
@task
def swarm_create():
    result = run('docker run --rm swarm create')
    token = result
    # save to disk
    with open('swarm_token', 'w') as f:
        f.write(token)
    run('docker run -d -p 4000:2375 swarm manage token://{}'.format(token))


# fab --roles agents swarm_join

# @runs_once
@roles('agents')
@task
def swarm_join():
    with open('swarm_token', 'r') as f:
        token = f.read()
    # run('docker run -d -p 2380:2375 swarm manage token://{}'.format(token))
    # manager = env.roledefs['managers'][0]
    result = run("cat /run/motd.dynamic | grep 'Internal ip' | awk '{print $4}'")
    internal_ip = result
    run('docker run -d swarm join --addr={}:2375 token://{}'.format(internal_ip, token))


# docker run -d swarm join --addr=<Node private DNS>:2375 token://xxxxxx

# Swarm auf dem Manager-Node erstellen
# docker run --rm swarm create
# Token kopieren!

# Swarm manager auf Manager-Node starten (Port 2380)
# docker run -d -p 2380:2375 swarm manage token://xxxxxxxx

# Auf den einzelnen Nodes: Swarm-Agents starten
# docker run -d swarm join --addr=<Node private DNS>:2375 token://xxxxxx



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
    run('apt-get install -y netcat-openbsd jq iputils-ping')
    # run('mkdir /tmp/curl || true')
    # with cd('/tmp/curl'):
    #     run('curl -SOL http://launchpadlibrarian.net/214117046/curl_7.43.0-1ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/214117047/libcurl3-gnutls_7.43.0-1ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/213509493/libnettle6_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/213509493/libnettle6_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/216006031/libgnutls-deb0-28_3.3.15-5ubuntu2_armhf.deb -SOL http://launchpadlibrarian.net/213509492/libhogweed4_3.1.1-4_armhf.deb -SOL http://launchpadlibrarian.net/206710934/libtasn1-6_4.5-2_armhf.deb')
    #     run('dpkg -i *.deb')
    #     run('apt-get -fy install')
    # run('rm /tmp/curl -rf')

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
    # result = run('uptime',
    #     shell=False, shell_escape=False, pty=False, quiet=True)
    result = run('uptime')
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
