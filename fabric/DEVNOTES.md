
$ docker run \
  --volume "$SSH_AUTH_SOCK:/tmp/ssh.sock" \
  --env SSH_AUTH_SOCK=/tmp/ssh.sock \
  --volume $PWD:/opt \
  -ti \
  --workdir /opt \
  local/fabric bash

$ cd fabric
$ fab --list
