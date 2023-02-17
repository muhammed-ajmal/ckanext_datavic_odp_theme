import pytest
from faker import Faker

import ckan.plugins.toolkit as tk

from ckanext.datavic_odp_theme.const import NOT_DOWNLOADABLE_FORMATS


fake = Faker()


@pytest.fixture
def resource_data():
    def func(**kwargs):
        data_dict = {
            "id": fake.uuid4(),
            "url": fake.url(),
            "name": fake.slug(fake.sentence(nb_words=5)),
            "format": "csv",
        }
        data_dict.update(kwargs)
        return data_dict

    return func


class TestHelpers:
    @pytest.mark.usefixtures("clean_db")
    def test_resource_formats_list(self, dataset_factory, resource_data):
        dataset_factory(
            resources=[
                resource_data(),
                resource_data(),
                resource_data(format="xml"),
                resource_data(format=""),
            ]
        )

        format_list: list[str] = tk.h.format_list()
        assert format_list == ["CSV", "XML"]

    @pytest.mark.usefixtures("clean_db")
    def test_resource_formats_list_no_resources(self):
        assert not tk.h.format_list()

    def test_is_resource_downloadable(self, resource_data):
        assert tk.h.is_resource_downloadable(resource_data())
        assert tk.h.is_resource_downloadable(
            resource_data(format="api", has_views=True)
        )
        assert tk.h.is_resource_downloadable(
            resource_data(format="api", url_type="upload")
        )

        for res_format in NOT_DOWNLOADABLE_FORMATS:
            assert not tk.h.is_resource_downloadable(resource_data(format=res_format))

    def test_organization_list(self):
        assert not tk.h.organization_list()
