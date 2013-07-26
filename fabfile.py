#!/usr/bin/python
# encoding: utf-8
"""
fabfile.py

Created by Luís Antônio Araújo Brito on 2013-05-25.

Release/Publish script with Fabric

Dependences:

~/.gitconfig or <flattenfields_dir>/.git/config
[alias]
        st = status
        ci = commit
        co = checkout
        lg1 = log --graph --all --format=format:'%C(bold blue)%h%C(reset) - %C(bold green)(%ar)%C(reset) %C(white)%s%C(reset) %C(bold white)— %an%C(reset)%C(bold yellow)%d%C(reset)' --abbrev-commit --date=relative
        lg2 = log --graph --all --format=format:'%C(bold blue)%h%C(reset) - %C(bold cyan)%aD%C(reset) %C(bold green)(%ar)%C(reset)%C(bold yellow)%d%C(reset)%n''          %C(white)%s%C(reset) %C(bold white)— %an%C(reset)' --abbrev-commit
        lg = !"git lg1"
"""
from fabric.api import *
from fabric.operations import *
from fabric.colors import *
from fabric.contrib.console import confirm
from fabric.contrib.files import *
import sys

env.project_name = u'Django Hstore Flattenfields'

REPLACE_CMD = "perl -pi.orig -e \"s/%(src)s/%(dst)s/\" %(file)s"


def _replace_in_file(src, dst, file_):
    local(REPLACE_CMD % dict(src=src, dst=dst, file=file_))

def release():
    """Create a tag release for an revision"""
    print yellow(">>> Creating a tag release")
    local("git tag")
    tagname = prompt("Enter a new tagname as according as above: ")

    print red('.... updating tag release at setup.py')
    _replace_in_file("version='.*'", "version='%s'" % tagname, 'setup.py')

    print red('.... versioning tag release')
    diff_ = local('git diff', capture=True)
    comment = prompt('Enter a bit comment for this release:')
    if diff_:
        print diff_
        if confirm("It's ok?", default=False):
            local('git add setup.py')
            local("git ci -m 'version %s - %s'" % (tagname, comment))
    local("git lg1 -n5")
    rev = prompt("Which revision you want release?")

    cmd_tag = "git tag -f %s %s -m '%s'" % (tagname, rev, comment)

    if confirm('%s # Create tag?' % cmd_tag, default=False):
        local(cmd_tag)

    if confirm('push to github?', default=False):
        local('git push origin master --tags -f')

def pub_release():
    """Publish release to PyPI. It's only used by mantainer"""
    local("python setup.py sdist upload -r http://pypi.python.org/pypi")


