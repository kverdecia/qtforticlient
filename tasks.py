import os

from invoke import task  # type: ignore


BASE_PATH = os.path.dirname(__file__)


@task
def clean(c):
    """
    Remove build artifacts
    """
    with c.cd(BASE_PATH):
        c.run("rm -fr build/")
        c.run("rm -fr dist/")


@task
def build_exe(c):
    clean(c)
    with c.cd(BASE_PATH):
        c.run("pyinstaller main.py --name=qtforticlient --icon ./resources/appicon.svg --noconfirm --onefile")


@task
def build_deb(c):
    path = os.path.join(BASE_PATH, 'dist')
    with c.cd(path):
        c.run('rm -rf deb_dist')
        c.run('mkdir deb_dist')
        with c.cd('deb_dist'):
            c.run('mkdir -p opt')
            c.run('mkdir -p opt/qtforticlient')
            c.run('mkdir -p usr/share/applications')
            c.run('mkdir -p usr/share/icons/hicolor/scalable/apps')
        c.run('cp ./qtforticlient deb_dist/opt/qtforticlient')
        c.run('cp ../qtforticlient/resources/appicon.svg deb_dist/usr/share/icons/hicolor/scalable/apps/qtforticlient.svg')
        c.run('cp ../qtforticlient/resources/qtforticlient.desktop deb_dist/usr/share/applications')
        c.run('find deb_dist/opt/qtforticlient -type f -exec chmod 644 -- {} +')
        c.run('find deb_dist/opt/qtforticlient -type d -exec chmod 755 -- {} +')
        c.run('find deb_dist/usr/share -type f -exec chmod 644 -- {} +')
        c.run('chmod +x deb_dist/opt/qtforticlient/qtforticlient')
        c.run('fpm -C deb_dist -s dir -t deb -n "qtforticlient" -v 0.1.0 -p qtforticlient.deb')


@task
def build(c):
    clean(c)
    build_exe(c)
    build_deb(c)


@task
def run(c):
    path = os.path.join(BASE_PATH, 'dist')
    with c.cd(path):
        c.run("./qtforticlient")
