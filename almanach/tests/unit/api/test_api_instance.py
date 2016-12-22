# Copyright 2016 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_entries
from hamcrest import has_key
from hamcrest import has_length

from almanach.core import exception
from almanach.tests.unit.api import base_api
from almanach.tests.unit.builders.entity import a
from almanach.tests.unit.builders.entity import instance


class ApiInstanceTest(base_api.BaseApi):

    def test_get_instances(self):
        self.instance_ctl.should_receive('list_instances') \
            .with_args('TENANT_ID', base_api.a_date_matching("2014-01-01 00:00:00.0000"),
                       base_api.a_date_matching("2014-02-01 00:00:00.0000")) \
            .and_return([a(instance().with_id('123'))])

        code, result = self.api_get('/project/TENANT_ID/instances',
                                    query_string={
                                        'start': '2014-01-01 00:00:00.0000',
                                        'end': '2014-02-01 00:00:00.0000'
                                    },
                                    headers={'X-Auth-Token': 'some token value'})

        assert_that(code, equal_to(200))
        assert_that(result, has_length(1))
        assert_that(result[0], has_key('entity_id'))
        assert_that(result[0]['entity_id'], equal_to('123'))

    def test_successful_instance_create(self):
        data = dict(id="INSTANCE_ID",
                    created_at="CREATED_AT",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_distro="A_DISTRIBUTION",
                    os_version="AN_OS_VERSION")

        self.instance_ctl.should_receive('create_instance') \
            .with_args(tenant_id="PROJECT_ID",
                       instance_id=data["id"],
                       create_date=data["created_at"],
                       flavor=data['flavor'],
                       os_type=data['os_type'],
                       distro=data['os_distro'],
                       version=data['os_version'],
                       name=data['name'],
                       metadata={}) \
            .once()

        code, result = self.api_post(
            '/project/PROJECT_ID/instance',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(code, equal_to(201))

    def test_instance_create_missing_a_param_returns_bad_request_code(self):
        data = dict(id="INSTANCE_ID",
                    created_at="CREATED_AT",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_version="AN_OS_VERSION")

        self.instance_ctl.should_receive('create_instance') \
            .never()

        code, result = self.api_post(
            '/project/PROJECT_ID/instance',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({"error": "The 'os_distro' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_instance_create_bad_date_format_returns_bad_request_code(self):
        data = dict(id="INSTANCE_ID",
                    created_at="A_BAD_DATE",
                    name="INSTANCE_NAME",
                    flavor="A_FLAVOR",
                    os_type="AN_OS_TYPE",
                    os_distro="A_DISTRIBUTION",
                    os_version="AN_OS_VERSION")

        self.instance_ctl.should_receive('create_instance') \
            .with_args(tenant_id="PROJECT_ID",
                       instance_id=data["id"],
                       create_date=data["created_at"],
                       flavor=data['flavor'],
                       os_type=data['os_type'],
                       distro=data['os_distro'],
                       version=data['os_version'],
                       name=data['name'],
                       metadata={}) \
            .once() \
            .and_raise(exception.DateFormatException)

        code, result = self.api_post(
            '/project/PROJECT_ID/instance',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries(
            {
                "error": "The provided date has an invalid format. "
                         "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
            }
        ))
        assert_that(code, equal_to(400))

    def test_successful_instance_resize(self):
        data = dict(date="UPDATED_AT",
                    flavor="A_FLAVOR")

        self.instance_ctl.should_receive('resize_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       flavor=data['flavor'],
                       resize_date=data['date']) \
            .once()

        code, result = self.api_put(
            '/instance/INSTANCE_ID/resize',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(code, equal_to(200))

    def test_successfull_instance_delete(self):
        data = dict(date="DELETE_DATE")

        self.instance_ctl.should_receive('delete_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       delete_date=data['date']) \
            .once()

        code, result = self.api_delete('/instance/INSTANCE_ID', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(code, equal_to(202))

    def test_instance_delete_missing_a_param_returns_bad_request_code(self):
        self.instance_ctl.should_receive('delete_instance') \
            .never()

        code, result = self.api_delete(
            '/instance/INSTANCE_ID',
            data=dict(),
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({"error": "The 'date' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_instance_delete_no_data_bad_request_code(self):
        self.instance_ctl.should_receive('delete_instance') \
            .never()

        code, result = self.api_delete('/instance/INSTANCE_ID', headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries({"error": "Invalid parameter or payload"}))
        assert_that(code, equal_to(400))

    def test_instance_delete_bad_date_format_returns_bad_request_code(self):
        data = dict(date="A_BAD_DATE")

        self.instance_ctl.should_receive('delete_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       delete_date=data['date']) \
            .once() \
            .and_raise(exception.DateFormatException)

        code, result = self.api_delete('/instance/INSTANCE_ID', data=data, headers={'X-Auth-Token': 'some token value'})
        assert_that(result, has_entries(
            {
                "error": "The provided date has an invalid format. "
                         "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
            }
        ))
        assert_that(code, equal_to(400))

    def test_instance_resize_missing_a_param_returns_bad_request_code(self):
        data = dict(date="UPDATED_AT")

        self.instance_ctl.should_receive('resize_instance') \
            .never()

        code, result = self.api_put(
            '/instance/INSTANCE_ID/resize',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({"error": "The 'flavor' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_instance_resize_bad_date_format_returns_bad_request_code(self):
        data = dict(date="A_BAD_DATE",
                    flavor="A_FLAVOR")

        self.instance_ctl.should_receive('resize_instance') \
            .with_args(instance_id="INSTANCE_ID",
                       flavor=data['flavor'],
                       resize_date=data['date']) \
            .once() \
            .and_raise(exception.DateFormatException)

        code, result = self.api_put(
            '/instance/INSTANCE_ID/resize',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries(
            {
                "error": "The provided date has an invalid format. "
                         "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
            }
        ))
        assert_that(code, equal_to(400))

    def test_rebuild_instance(self):
        instance_id = 'INSTANCE_ID'
        data = {
            'distro': 'A_DISTRIBUTION',
            'version': 'A_VERSION',
            'os_type': 'AN_OS_TYPE',
            'rebuild_date': 'UPDATE_DATE',
        }
        self.instance_ctl.should_receive('rebuild_instance') \
            .with_args(
            instance_id=instance_id,
            distro=data.get('distro'),
            version=data.get('version'),
            os_type=data.get('os_type'),
            rebuild_date=data.get('rebuild_date')) \
            .once()

        code, result = self.api_put(
            '/instance/INSTANCE_ID/rebuild',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )

        assert_that(code, equal_to(200))

    def test_rebuild_instance_missing_a_param_returns_bad_request_code(self):
        data = {
            'distro': 'A_DISTRIBUTION',
            'rebuild_date': 'UPDATE_DATE',
        }

        self.instance_ctl.should_receive('rebuild_instance') \
            .never()

        code, result = self.api_put(
            '/instance/INSTANCE_ID/rebuild',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries({"error": "The 'version' param is mandatory for the request you have made."}))
        assert_that(code, equal_to(400))

    def test_rebuild_instance_bad_date_format_returns_bad_request_code(self):
        instance_id = 'INSTANCE_ID'
        data = {
            'distro': 'A_DISTRIBUTION',
            'version': 'A_VERSION',
            'os_type': 'AN_OS_TYPE',
            'rebuild_date': 'A_BAD_UPDATE_DATE',
        }

        self.instance_ctl.should_receive('rebuild_instance') \
            .with_args(instance_id=instance_id, **data) \
            .once() \
            .and_raise(exception.DateFormatException)

        code, result = self.api_put(
            '/instance/INSTANCE_ID/rebuild',
            data=data,
            headers={'X-Auth-Token': 'some token value'}
        )
        assert_that(result, has_entries(
            {
                "error": "The provided date has an invalid format. "
                         "Format should be of yyyy-mm-ddThh:mm:ss.msZ, ex: 2015-01-31T18:24:34.1523Z"
            }
        ))
