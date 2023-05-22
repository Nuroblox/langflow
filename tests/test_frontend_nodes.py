from langflow.template.frontend_node.base import FrontendNode
from langflow.template.template.base import Template
import pytest
from langflow.template.field.base import TemplateField


@pytest.fixture
def sample_template_field() -> TemplateField:
    return TemplateField(name="test_field", field_type="str")


@pytest.fixture
def sample_template(sample_template_field: TemplateField) -> Template:
    return Template(type_name="test_template", fields=[sample_template_field])


@pytest.fixture
def sample_frontend_node(sample_template: Template) -> FrontendNode:
    return FrontendNode(
        template=sample_template,
        description="test description",
        base_classes=["base_class1", "base_class2"],
        name="test_frontend_node",
    )


def test_template_field_defaults(sample_template_field: TemplateField):
    assert sample_template_field.field_type == "str"
    assert sample_template_field.required is False
    assert sample_template_field.placeholder == ""
    assert sample_template_field.is_list is False
    assert sample_template_field.show is True
    assert sample_template_field.multiline is False
    assert sample_template_field.value is None
    assert sample_template_field.suffixes == []
    assert sample_template_field.file_types == []
    assert sample_template_field.content is None
    assert sample_template_field.password is False
    assert sample_template_field.name == "test_field"


def test_template_to_dict(
    sample_template: Template, sample_template_field: TemplateField
):
    template_dict = sample_template.to_dict()
    assert template_dict["_type"] == "test_template"
    assert len(template_dict) == 3  # _type, test_field, root_field
    assert "test_field" in template_dict
    assert "type" in template_dict["test_field"]
    assert "required" in template_dict["test_field"]


def test_frontend_node_to_dict(sample_frontend_node: FrontendNode):
    node_dict = sample_frontend_node.to_dict()
    assert len(node_dict) == 1
    assert "test_frontend_node" in node_dict
    assert "description" in node_dict["test_frontend_node"]
    assert "template" in node_dict["test_frontend_node"]
    assert "base_classes" in node_dict["test_frontend_node"]
