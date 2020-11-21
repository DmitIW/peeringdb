import os

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings


from .util import SettingsCase
from peeringdb_server import signals, models, serializers
from peeringdb_server import settings as pdb_settings
from mainsite.settings import (
    _set_option,
    set_from_env,
    set_default,
)


class TestAutoVerifyUser(SettingsCase):
    settings = {"AUTO_VERIFY_USERS": True}

    def test_setting(self):
        user = get_user_model().objects.create_user(
            "user_a", "user_a@localhost", "user_a"
        )
        signals.new_user_to_guests(None, user)
        assert user.is_verified_user == True
        assert user.status == "ok"


class TestAutoApproveAffiliation(SettingsCase):
    settings = {"AUTO_APPROVE_AFFILIATION": True}

    def test_setting(self):

        org = models.Organization.objects.create(name="Test Org", status="ok")
        net = models.Network.objects.create(
            name="Test Net", org=org, asn=63311, status="ok"
        )
        user = get_user_model().objects.create_user(
            "user_a", "user_a@localhost", "user_a"
        )
        user_b = get_user_model().objects.create_user(
            "user_b", "user_b@localhost", "user_b"
        )
        user.set_verified()
        user_b.set_verified()

        uoar = models.UserOrgAffiliationRequest.objects.create(
            user=user, org=org, asn=net.asn
        )
        assert user.is_org_admin(org) == True

        uoar = models.UserOrgAffiliationRequest.objects.create(user=user, asn=63312)
        net = models.Network.objects.get(asn=63312)
        assert user.is_org_admin(net.org) == True

        uoar = models.UserOrgAffiliationRequest.objects.create(
            user=user, org_name="Test Org 2"
        )
        org = models.Organization.objects.get(name="Test Org 2")
        assert user.is_org_admin(org) == True

        uoar = models.UserOrgAffiliationRequest.objects.create(user=user_b, asn=63312)
        assert user_b.is_org_admin(net.org) == False
        assert user_b.is_org_member(net.org) == False


def test_set_option():
    context = {}
    _set_option("TEST_SETTING", "hello", context)
    assert context["TEST_SETTING"] == "hello"


def test_set_option_w_env_var():
    """
    Environment variables take precedence over provided options
    """
    context = {}
    os.environ["TEST_SETTING"] = "world"
    _set_option("TEST_SETTING", "hello", context)
    assert context["TEST_SETTING"] == "world"


def test_set_option_coerce_env_var():
    """
    We coerce the environment variable to the same type
    as the provided default.
    """
    context = {}
    # env variables can never be set as integers
    os.environ["TEST_SETTING"] = "123"

    # setting an option with a default integer will coerce the env
    # variable as well (fix for issue #888)
    _set_option("TEST_SETTING", 321, context)
    assert context["TEST_SETTING"] == 123

    # setting an option with a default string will coerce the env
    # variable as well
    _set_option("TEST_SETTING", "321", context)
    assert context["TEST_SETTING"] == "123"

    _set_option("TEST_SETTING", 123.1, context)
    assert context["TEST_SETTING"] == 123.0
