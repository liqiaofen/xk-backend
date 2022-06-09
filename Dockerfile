ARG PYTHON_VERSION=3.9.2
#ARG 指令有生效范围，如果在 FROM 指令之前指定，那么只能用于 FROM 指令中
#多阶段构建(Multi-stage builds):主要依赖于新提供的关键字：from 和 as
#多阶段构建的Dockerfile看起来像是把两个或者更多的Dockerfile合并在了一起，这也即多阶段的意思
FROM python:${PYTHON_VERSION}

# Install apt packages
#RUN apt-get update && apt-get install --no-install-recommends -y \
#  # dependencies for building Python packages
#  build-essential \
#  # psycopg2 dependencies
#  libpq-dev

# set environment variables
# 防止Python将pyc文件写入光盘（等效的python -B选项）
ENV PYTHONDONTWRITEBYTECODE 1  
# 防止Python缓冲stdout和stderr（相当于python -u选项）
ENV PYTHONUNBUFFERED 1

# 安装psycopg2所需要的适当的软件包
# 有关基于Alpine的Dokcer镜像中安装Psycopg2的问题
# https://github.com/psycopg/psycopg2/issues/684
# RUN apk update \
#     && apk add postgresql-dev gcc python3-dev musl-dev



ARG APP_HOME=/app
RUN mkdir ${APP_HOME}
RUN mkdir -p ${APP_HOME}/logs
RUN mkdir ${APP_HOME}/staticfiles
WORKDIR ${APP_HOME}

COPY . ${APP_HOME}

#COPY requirements.txt ${APP_HOME}
RUN pip install --upgrade pip
#安装poetry
RUN pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com poetry
#禁用poetry创建虚拟环境， 并导入安装包
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-dev

RUN sed -i 's/\r$//g' ${APP_HOME}/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# run entrypoint.sh
ENTRYPOINT [ "/app/entrypoint.sh" ]