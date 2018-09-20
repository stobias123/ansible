#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2012, Michael DeHaan <michael.dehaan@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
- perforce:
    p4_path: p4://Ansible/...
    dest: /src/Ansible
    force: yes
    tags: 1.0-release
'''

import os
import re

from ansible.module_utils.basic import AnsibleModule


class Perforce(P4):
    def __init__(self, module, dest, repo, tag, username, password):
        self.module = module
        self.dest = dest
        self.repo = repo
        self.tag = tag
        self.username = username
        self.password = password

    def get_tag(self):
        '''tag and of perforce repo directory.'''
        return False

def main():
    module = AnsibleModule(
        argument_spec=dict(
            dest=dict(type='path'),
            repo=dict(type='str', required=True, aliases=['repository']),
            tag=dict(type='str', default='HEAD'),
            force=dict(type='bool', default=False),
            username=dict(type='str'),
            password=dict(type='str', no_log=True),
        ),
        supports_check_mode=True,
    )

    dest = module.params['dest']
    repo = module.params['repo']
    tag = module.params['tag']
    force = module.params['force']
    username = module.params['username']
    password = module.params['password']


    if not dest and (checkout or update or export):
        module.fail_json(msg="the destination directory must be specifiedo")

    p4 = Perforce(module, dest, repo, revision, username, password, svn_path)

    if not export and not update and not checkout:
        module.exit_json(changed=False, after=svn.get_remote_revision())
    if export or not os.path.exists(dest):
        before = None
        local_mods = False
        if module.check_mode:
            module.exit_json(changed=True)
        elif not export and not checkout:
            module.exit_json(changed=False)
        if not export and checkout:
            svn.checkout()
            files_changed = True
        else:
            svn.export(force=force)
            files_changed = True
    elif svn.is_svn_repo():
        # Order matters. Need to get local mods before switch to avoid false
        # positives. Need to switch before revert to ensure we are reverting to
        # correct repo.
        if not update:
            module.exit_json(changed=False)
        if module.check_mode:
            if svn.has_local_mods() and not force:
                module.fail_json(msg="ERROR: modified files exist in the repository.")
            check, before, after = svn.needs_update()
            module.exit_json(changed=check, before=before, after=after)
        files_changed = False
        before = svn.get_revision()
        local_mods = svn.has_local_mods()
        if switch:
            files_changed = svn.switch() or files_changed
        if local_mods:
            if force:
                files_changed = svn.revert() or files_changed
            else:
                module.fail_json(msg="ERROR: modified files exist in the repository.")
        files_changed = svn.update() or files_changed
    elif in_place:
        before = None
        svn.checkout(force=True)
        files_changed = True
        local_mods = svn.has_local_mods()
        if local_mods and force:
            svn.revert()
    else:
        module.fail_json(msg="ERROR: %s folder already exists, but its not a subversion repository." % (dest,))

    if export:
        module.exit_json(changed=True)
    else:
        after = svn.get_revision()
        changed = files_changed or local_mods
        module.exit_json(changed=changed, before=before, after=after)


if __name__ == '__main__':
    main()

from P4 import P4,P4Exception
p4 = P4()
p4.client = "example"
p4.port = "1666"
p4.user = "fooser"
client_root = '/foo/bar'

p4.connect()
client = p4.fetch_client()
client._root = client_root
#p4.save_client(p4)
with p4.temp_client('temp',client) as t:
    p4.run_sync()




perforce_template = '''

Client: temp_client
Owner:  user
Host:   bleh
Description:
        Created by ansible.
Root:   /Users/fooser/p4test2
Options:        noallwrite noclobber nocompress unlocked nomodtime normdir
SubmitOptions:  submitunchanged
LineEnd:        local
View:
        //depot/... //bleh/test.txt
'''
p4.run_sync('-f')
# Convert client spec into a Python dictionary
# with p4.temp_client("ansible",perforce_template) as t:
#   client._root = client_root
#   p4.run_sync('-f')
