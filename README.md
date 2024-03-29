# efaLive development Docker file

Here you can find a Docker file that creates a development environment for efaLive. For more information about Docker, you can visit the [Docker pages](http://docker.io/). Information about efaLive can be found on [my homepage](https://www.hannay.de/en/efalive/).

## Binaries and documentation
For more information about efaLive, have a look to the efaLive documentation on [my homepage](https://www.hannay.de/en/efalive/). There you can also find efaLive CD images for download.

## Related projects
* [Debian GNU/Linux project](http://www.debian.org/)
* [efaLive Docker](https://github.com/kayhannay/efalive_docker) - the Docker file to create an efaLive development environment (this project)
* [efaLive CD](https://github.com/kayhannay/efalive_cd) - the live CD build configuration
* [efaLive PI](https://github.com/kayhannay/efalive_pi) - efaLive image for RaspberryPi
* [efaLive](https://github.com/kayhannay/efalive) - the glue code between Debian and the efa software
* [efa 2](https://github.com/kayhannay/efa2) - the Debian package configuration of the efa software
* [efa](http://efa.nmichael.de/) - the rowing and canoeing log book software

## Requirements
You need to have Docker installed on your system. To develop and build an efaLive image, you need to clone the efaLive CD, efaLive and efa 2 projects to some directory on your PC. This directory is used later on for the Docker container.

## How to build
You can download the Docker image or build it yourself. Change to the efaLive Docker project directory and run the following command:

```shell
docker build -t efalive/efalive-dev:bookworm .
```

You of course might change the tag name in the command above to your wishes, it is just an example.

## How to run
Run the docker container from the Docker registry by using the following command:

```shell
docker run -it -v <PATH_TO_EFALIVE_REPOSITORIES>:/home/efalive/development --name efalive-dev --privileged=true ghcr.io/kayhannay/efalive_docker/efalive-development:latest
```

or, if you have built the image locally:

```shell
docker run -it -v <PATH_TO_EFALIVE_REPOSITORIES>:/home/efalive/development --name efalive-dev --privileged=true efalive/efalive-dev:bookworm
```

Replace <PATH_TO_EFALIVE_REPOSITORIES> with the name of the folder where you have cloned or will clone the efaLive projects to. Again, you can replace the name for the container and the tag to whatever you want.

After you have started the command above, you will find yourself inside the docker container as user root. The path that you specified by <PATH_TO_EFALIVE_REPOSITORIES> is mapped to 'development' in the home directory of 'efalive'.

If you want to exit the container, you can use

```shell
exit
```

To re-start it use

```shell
docker start -ai efalive-dev
```

Now you can build for example a efaLive image using the following commands:

```shell
cd /home/efalive/development/efalive_cd
lb clean
lb build
```
