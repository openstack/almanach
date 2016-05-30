from hamcrest import assert_that, equal_to

from base_api_testcase import BaseApiTestCase


class ApiInstanceEntityTest(BaseApiTestCase):
    def test_head_entity_by_id_with_entity_return_200(self):
        instance_id = self._create_instance_entity()
        response = self.almanachHelper.head(url="{url}/entity/{instance_id}",
                                            instance_id=instance_id)

        assert_that(response.status_code, equal_to(200))

    def test_head_entity_by_id__without_entity_return_404(self):
        instance_id = "some_uuid"
        response = self.almanachHelper.head(url="{url}/entity/{instance_id}",
                                            instance_id=instance_id)

        assert_that(response.status_code, equal_to(404))
