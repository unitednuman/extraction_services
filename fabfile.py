from fabric import task


@task
def dev(context):
    context.environment = 'dev'


@task
def live(context):
    context.environment = 'live'


@task
def deploy(context):
    context.run('docker-compose  -f deploy/{env}/docker-compose.yml up --build -d'.format(env=context.environment),
                replace_env=False, pty=True)


@task
def logs(context):
    context.run('docker-compose  -f deploy/{env}/docker-compose.yml logs -f'.format(env=context.environment),
                replace_env=False, pty=True)


@task
def update(context, branch='main'):
    context.run('git pull origin {branch}'.format(branch=branch), replace_env=False, pty=True)
