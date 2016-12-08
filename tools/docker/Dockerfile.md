## DockerFile构建镜像

docker镜像的构建，一般都是采用Dockerfile的形式来构建，大部分情况下并不会使用docker commit。整个过程分为两步，第一步，Dockerfile的编写，第二步使用`docker build`命令，构建镜像。

在构建时，Dockerfile文件的第一条指令必须是FROM命令。然后可以使用RUN命令对这个镜像操作。最后可以使用EXPOSE来告诉Docker容器内应用程序会使用哪个端口。

## 指令说明

- CMD 用于指定容器启动时要运行的命令,但是需要说明的是，docker run命令中指定的参数会覆盖CMD指令
```
CMD ["/bin/ls", "-l"]
```
- ENTRYPOINT
ENTRYPOINT指令和CMD指令比较相似，在ENTRYPOINT中也是以数组的形式指定参数。但是CMD指令中的参数会被run命令中的参数覆盖，但是ENTRYPOINT中的参数并不会被run命令覆盖，run命令中指定的参数会被当做参数再次传递给ENTRYPOINT指令中指定的命令。
```
#在entrypoint中指定了nginx
ENTRYPOINT ["/usr/sbin/nginx"]
#在启动时为nginx指定参数
sudo docker run -t -i xxx/xxx -g "daemon off"
```
- WORKDIR
WORKDIR命令用来在创建容器时，在容器内部设置一个工作目录，ENTRYPOINT或者CMD命令将在该目录下运行。同时也可以在运行时使用-w 标识覆盖工作目录。
- ENV
ENV 命令用来在镜像构建过程中设置环境变量，可以在一行中指定多个环境变量。 同时也可以使用-e参数，在运行时指定环境变量，如`WEB_PORT=8080`
```
ENV RVM_PATH /home/rvm RVM_XXX xxxx
```
- USER
USER 指令用来指定该镜像会以什么样的用户去运行。即指定运行时的用户名。
- VOLUME
该指令用来向基于镜像创建的容器添加卷。
- ADD
ADD 命令用来将构建环境下得文件和目录复制到镜像中。
```
VOLUME ["/opt/local"]
```

### 待核实的问题

1. 如果USER指定的用户不存在会怎么办？
2. 容器内的卷和容器所在机器的文件系统之间的关系？