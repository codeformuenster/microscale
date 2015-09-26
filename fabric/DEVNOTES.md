
```bash
$ docker build -t local/fabric .
```

```bash
$ docker run \
  --volume "$SSH_AUTH_SOCK:/tmp/ssh.sock" \
  --env SSH_AUTH_SOCK=/tmp/ssh.sock \
  --volume $PWD:/opt \
  -ti \
  --workdir /opt \
  local/fabric bash
```

```bash
$ cd fabric
$ fab --list
```

topbeat

docker run \
  --volume "$PWD":/usr/src/myapp \
  --workdir /usr/src/myapp \
  --env GOOS=linux \
  --env GOARCH=arm \
  --env GOARM=7 \
  golang:1.3-cross make

  docker run \
    --volume "$PWD":/usr/src/myapp \
    --workdir /usr/src/myapp \
    --env "GOBIN=$GOPATH/bin" \
    --env "PATH=$GOPATH:$GOBIN:$PATH" \
    --env GOARCH=arm \
    golang:1.4-cross make


    docker run \
      --volume "$PWD":/usr/src/myapp \
      --workdir /usr/src/myapp \
      --env GOARCH=arm \
      golang:1.4-cross make


docker run --rm -v "$PWD":/usr/src/myapp -w /usr/src/myapp -e GOOS=linux -e GOARCH=arm golang:1.3-cross make
