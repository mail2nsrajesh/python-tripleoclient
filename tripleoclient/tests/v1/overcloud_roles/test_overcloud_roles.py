#   Copyright 2017 Red Hat, Inc.
#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

import mock

from tripleoclient.exceptions import NotFound
from tripleoclient.tests.v1.overcloud_deploy import fakes
from tripleoclient.v1 import overcloud_roles


class TestOvercloudRolesListAvailable(fakes.TestDeployOvercloud):

    def setUp(self):
        super(TestOvercloudRolesListAvailable, self).setUp()
        self.cmd = overcloud_roles.RoleList(self.app, None)

    @mock.patch('os.path.realpath')
    def test_action(self, realpath_mock):
        realpath_mock.return_value = '/foo'
        get_roles_mock = mock.MagicMock()
        get_roles_mock.return_value = ['a', 'b']
        self.cmd._get_roles = get_roles_mock

        arglist = []
        verifylist = [
            ('roles_path', '/usr/share/openstack-tripleo-heat-templates/roles')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        get_roles_mock.assert_called_once_with('/foo')

    @mock.patch('os.path.realpath')
    def test_action_role_path(self, realpath_mock):
        realpath_mock.return_value = '/tmp'
        get_roles_mock = mock.MagicMock()
        get_roles_mock.return_value = ['a', 'b']
        self.cmd._get_roles = get_roles_mock

        arglist = ['--roles-path', '/tmp']
        verifylist = [
            ('roles_path', '/tmp')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        get_roles_mock.assert_called_once_with('/tmp')


class TestOvercloudRolesGenerateData(fakes.TestDeployOvercloud):

    def setUp(self):
        super(TestOvercloudRolesGenerateData, self).setUp()
        self.cmd = overcloud_roles.RolesGenerate(self.app, None)

    @mock.patch('shutil.copyfileobj')
    @mock.patch('tripleoclient.v1.overcloud_roles.open')
    @mock.patch('os.path.realpath')
    def test_action(self, realpath_mock, open_mock, copy_mock):
        realpath_mock.return_value = '/tmp'
        get_roles_mock = mock.MagicMock()
        get_roles_mock.return_value = ['Controller', 'Compute']
        capture_mock = mock.MagicMock()
        self.cmd._get_roles = get_roles_mock
        self.cmd._capture_output = capture_mock

        arglist = ['--roles-path', '/tmp', 'Controller', 'Compute']
        verifylist = [
            ('roles_path', '/tmp'),
            ('roles', ['Controller', 'Compute'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        capture_mock.assert_called_once_with(None)
        get_roles_mock.assert_called_once_with('/tmp')
        open_mock.assert_any_call('/tmp/Controller.yaml', 'r')
        open_mock.assert_any_call('/tmp/Compute.yaml', 'r')

    @mock.patch('shutil.copyfileobj')
    @mock.patch('tripleoclient.v1.overcloud_roles.open')
    @mock.patch('os.path.realpath')
    def test_action_with_outputfile(self, realpath_mock, open_mock, copy_mock):
        realpath_mock.return_value = '/tmp'
        get_roles_mock = mock.MagicMock()
        get_roles_mock.return_value = ['Controller', 'Compute']
        capture_mock = mock.MagicMock()
        self.cmd._get_roles = get_roles_mock
        self.cmd._capture_output = capture_mock

        arglist = ['--roles-path', '/tmp', '-o', 'foo.yaml',
                   'Controller', 'Compute']
        verifylist = [
            ('output_file', 'foo.yaml'),
            ('roles_path', '/tmp'),
            ('roles', ['Controller', 'Compute'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        capture_mock.assert_called_once_with('foo.yaml')
        get_roles_mock.assert_called_once_with('/tmp')
        open_mock.assert_any_call('/tmp/Controller.yaml', 'r')
        open_mock.assert_any_call('/tmp/Compute.yaml', 'r')

    @mock.patch('os.path.realpath')
    def test_action_with_invald_roles(self, realpath_mock):
        realpath_mock.return_value = '/tmp'
        get_roles_mock = mock.MagicMock()
        get_roles_mock.return_value = ['Controller', 'Compute']
        capture_mock = mock.MagicMock()
        self.cmd._get_roles = get_roles_mock
        self.cmd._capture_output = capture_mock

        arglist = ['--roles-path', '/tmp', 'Foo', 'Bar']
        verifylist = [
            ('roles_path', '/tmp'),
            ('roles', ['Foo', 'Bar'])
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(NotFound, self.cmd.take_action, parsed_args)
        capture_mock.assert_called_once_with(None)
        get_roles_mock.assert_called_once_with('/tmp')


class TestOvercloudRoleInfo(fakes.TestDeployOvercloud):

    def setUp(self):
        super(TestOvercloudRoleInfo, self).setUp()
        self.cmd = overcloud_roles.RoleShow(self.app, None)

    @mock.patch('yaml.safe_load')
    @mock.patch('tripleoclient.v1.overcloud_roles.open')
    @mock.patch('os.path.realpath')
    def test_action(self, realpath_mock, open_mock, yaml_mock):
        realpath_mock.return_value = '/tmp'
        yaml_mock.return_value = [{'name': 'foo', 'Services': ['a', 'b']}]

        arglist = ['--roles-path', '/tmp', 'foo']
        verifylist = [
            ('roles_path', '/tmp'),
            ('role', 'foo')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.cmd.take_action(parsed_args)
        open_mock.assert_called_once_with('/tmp/foo.yaml', 'r')

    @mock.patch('tripleoclient.v1.overcloud_roles.open')
    @mock.patch('os.path.realpath')
    def test_action_invalid_role(self, realpath_mock, open_mock):
        realpath_mock.return_value = '/tmp'
        open_mock.side_effect = IOError('bar')

        arglist = ['--roles-path', '/tmp', 'foo']
        verifylist = [
            ('roles_path', '/tmp'),
            ('role', 'foo')
        ]
        parsed_args = self.check_parser(self.cmd, arglist, verifylist)

        self.assertRaises(NotFound, self.cmd.take_action, parsed_args)
        open_mock.assert_called_once_with('/tmp/foo.yaml', 'r')
