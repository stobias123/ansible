#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

## TODO: Load p4 variables by default.
## TODO: add tag support

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'core'}
from P4 import P4,P4Exception

DOCUMENTATION = '''
---
module: subversion
short_description: Deploys a subversion repository
description:
   - Deploy given repository URL / revision to dest. If dest exists, update to the specified revision, otherwise perform a checkout.
version_added: "0.7"
author:
- Dane Summers (@dsummersl) <njharman@gmail.com>
notes:
   - Requires I(svn) to be installed on the client.
   - This module does not handle externals.
options:
  repo:
    description:
      - The subversion URL to the repository.
    required: true
    aliases: [ name, repository ]
  dest:
    description:
      - Absolute path where the repository should be deployed.
    required: true
  tag:
    description:
      - Specific tag to checkout.
    default: HEAD
    aliases: [ version ]
  force:
    description:
      - If C(yes), modified files will be discarded. If C(no), module will fail if it encounters modified files.
        Prior to 1.9 the default was C(yes).
    type: bool
    default: "no"
  username:
    description:
      - C(--username) parameter passed to svn.
  password:
    description:
      - C(--password) parameter passed to svn.
'''

EXAMPLES = '''
- name: Checkout perforce repository to specified folder
  perforce:
    p4_path: p4://Ansible/...
    dest: /src/Ansible

- name: Get information about the repository whether or not it has already been cloned locally
  perforce:
    username: fooser
    password: basswd
    dest: /path/to/target/dir
    dept_src_path: "//depot/..."
    force: yes
    tags: 1.0-release
'''

import os
import re

from ansible.module_utils.basic import AnsibleModule
from P4 import P4,P4Exception

class Perforce():
    def __init__(self, module, dest_path, depot_src_path, tag, port, username, password):
        self.p4 = P4()
        self.p4.client = "ansible_perforce_"
        #self.tag = tag
        self.p4.port = port
        self.p4.user = username
        self.p4.password = password

        self.p4.connect()
        self.p4.run_login()
        client = self.p4.fetch_client()
        client._root = dest_path
        self.p4.save_client(client)

    def force_sync(self):
        self.p4.run_sync('-f')

    def sync(self):
        self.p4.run_sync()

    def destroy(self):
        self.p4.delete_client(self.p4.client)

    def get_tag(self):
        '''tag and of perforce repo directory.'''
        return False

def main():
    print('hello world')
    module = AnsibleModule(
        argument_spec=dict(
            dest=dict(type='path'),
            depot_src_path=dict(type='str', required=True),
            tag=dict(type='str', default='HEAD'),
            port=dict(type='str', default='1666'),
            force=dict(type='bool', default=False),
            username=dict(type='str'),
            password=dict(type='str', no_log=True),
        ),
        supports_check_mode=True,
    )

    dest = module.params['dest']
    depot_src_path = module.params['depot_src_path']
    tag = module.params['tag']
    force = module.params['force']
    port = module.params['port']
    username = module.params['username']
    password = module.params['password']


    if not dest and (checkout or update or export):
        module.fail_json(msg="the destination directory must be specifiedo")

    p4 = Perforce(module, dest, depot_src_path, tag, port, username, password)

    before = None
    if not os.path.exists(dest):
        print('we dont have that path')
        before = None
        os.mkdir(dest)
        if module.check_mode:
            module.exit_json(changed=True)
    if force:
        print('force sync')
        p4.force_sync()
        files_changed = True
    else:
        print('were in else block')
        p4.sync()
        files_changed = True
        changed = files_changed or local_mods
        module.exit_json(changed=changed, before=before, after=after)
    p4.destroy()

if __name__ == '__main__':
    main()
# Convert client spec into a Python dictionary
# with p4.temp_client("ansible",perforce_template) as t:
#   client._root = client_root
#   p4.run_sync('-f')
