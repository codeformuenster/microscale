# Pull & tag armhf base images

## Building

You need the `docker:1.8` and `docker:dind` base images:

	docker pull armhfbuild/docker:1.8
	docker pull armhfbuild/docker:dind
	docker tag -f armhfbuild/docker:1.8 docker:1.8
	docker tag -f armhfbuild/docker:dind docker:dind

Then build the image:

	docker build -t armhfbuild/get-base-images .

## Usage

Run a containerized Docker daemon:

	docker run --privileged -d --name dockerd -v $PWD/my-varlibdocker:/var/lib/docker docker:dind

Then get the base images in there:

	docker run -it --rm --link dockerd:docker armhfbuild/get-base-images

You should now be able to list the images:

	docker run --rm --link dockerd:docker docker:1.8 docker images
