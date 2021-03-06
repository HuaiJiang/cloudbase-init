# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2013 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
import unittest

from oslo.config import cfg

from cloudbaseinit.plugins.windows import sethostname
from cloudbaseinit.tests.metadata import fake_json_response

CONF = cfg.CONF


class SetHostNamePluginPluginTests(unittest.TestCase):

    def setUp(self):
        self._sethostname_plugin = sethostname.SetHostNamePlugin()
        self.fake_data = fake_json_response.get_fake_metadata_json(
            '2013-04-04')

    @mock.patch('cloudbaseinit.osutils.factory.get_os_utils')
    def _test_execute(self, mock_get_os_utils, hostname_exists,
                      new_hostname_length=1):
        mock_service = mock.MagicMock()
        mock_osutils = mock.MagicMock()
        fake_shared_data = 'fake data'
        new_hostname = 'x' * new_hostname_length
        if hostname_exists:
            mock_service.get_host_name.return_value = new_hostname
        else:
            mock_service.get_host_name.return_value = None
        CONF.set_override('netbios_host_name_compatibility', True)
        mock_get_os_utils.return_value = mock_osutils
        mock_osutils.set_host_name.return_value = False
        response = self._sethostname_plugin.execute(mock_service,
                                                    fake_shared_data)
        mock_service.get_host_name.assert_caled_once_with()
        if hostname_exists is True:
            length = sethostname.NETBIOS_HOST_NAME_MAX_LEN
            mock_get_os_utils.assert_called_once_with()
            hostname = new_hostname.split('.', 1)[0]
            if len(new_hostname) > length:
                hostname = hostname[:length]
            mock_osutils.set_host_name.assert_called_once_with(hostname)

        self.assertEqual(response, (1, False))

    def test_execute_hostname_to_be_truncated(self):
        self._test_execute(
            hostname_exists=True,
            new_hostname_length=sethostname.NETBIOS_HOST_NAME_MAX_LEN + 1)

    def test_execute_no_truncate_needed(self):
        self._test_execute(
            hostname_exists=True,
            new_hostname_length=sethostname.NETBIOS_HOST_NAME_MAX_LEN)

    def test_execute_no_hostname(self):
        self._test_execute(hostname_exists=False)
