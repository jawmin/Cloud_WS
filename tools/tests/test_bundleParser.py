from unittest import TestCase
from tools.bundle_parser import BundleParser, BundleError
import json

__author__ = 'benoit'


class TestBundleParser(TestCase):
    def setUp(self):
        self.empty = ""
        self.noservice = json.loads('{"envExport": {"relations": [["wordpress:db","mysql:db"]]}}')
        self.norelation = json.loads('{"envExport": {"services": {'
                                     '"mysql": {"charm": "cs:precise/mysql-27","num_units": 1},'
                                     '"wordpress": {"charm": "cs:precise/wordpress-20","num_units": 1}}}}')
        self.correct = json.loads('{"envExport": {"services": {'
                                  '"mysql": {"charm": "cs:precise/mysql-27","num_units": 1},'
                                  '"wordpress": {"charm": "cs:precise/wordpress-20","num_units": 1, "expose": true}},'
                                  '"relations": [["wordpress:db","mysql:db"], ["wordpress","mysql"]]}}')
        self.nounit = json.loads('{"envExport": {"services": {'
                                 '"mysql": {"charm": "cs:precise/mysql-27"},'
                                 '"wordpress": {"charm": "cs:precise/wordpress-20"}},'
                                 '"relations": [["wordpress:db","mysql:db"]]}}')
        self.nocharm = json.loads('{"envExport": {"services": {'
                                  '"mysql": {"num_units": 1},'
                                  '"wordpress": {"num_units": 1}},'
                                  '"relations": [["wordpress:db","mysql:db"]]}}')

    def test_getservice(self):
        # test bundle empty
        self.assertRaises(BundleError, BundleParser, self.empty)

        # test bundle no service section
        bundle = BundleParser(self.noservice)
        self.assertRaises(BundleError, bundle.getservice, "fake")

        # test bundle service not found
        bundle = BundleParser(self.correct)
        self.assertRaises(BundleError, bundle.getservice, "fake")

        # test bundle service exists
        self.assertIsNotNone(bundle.getservice("mysql"))

    def test_listservices(self):
        # test no services
        bundle = BundleParser(self.noservice)
        if bundle.listservices():
            self.fail()

        # test services found
        bundle = BundleParser(self.correct)
        if not bundle.listservices():
            self.fail()

    def test_getrelations(self):
        # no relation section
        bundle = BundleParser(self.norelation)
        if bundle.getrelations():
            self.fail()

        # complete relation
        bundle = BundleParser(self.correct)
        if not bundle.getrelations():
            self.fail()

    def test__serviceexists(self):
        # test bundle no service section
        bundle = BundleParser(self.noservice)
        self.assertFalse(bundle._serviceexists("fake"))

        # test bundle service not found
        bundle = BundleParser(self.correct)
        self.assertFalse(bundle._serviceexists("fake"))

        # test bundle service exists
        self.assertTrue(bundle._serviceexists("mysql"))

    def test_getnumberunits(self):
        # no units
        bundle = BundleParser(self.nounit)
        self.assertRaises(BundleError, bundle.getnumberunits, "mysql")

        # has units
        bundle = BundleParser(self.correct)
        self.assertEqual(1, bundle.getnumberunits("mysql"))

    def test_getcharmname(self):
        # no charm
        bundle = BundleParser(self.nocharm)
        self.assertRaises(BundleError, bundle.getcharmname, "mysql")

        # has charm
        bundle = BundleParser(self.correct)
        self.assertIsNotNone(bundle.getcharmname("mysql"))

    def test_isexposed(self):
        # is not exposed
        bundle = BundleParser(self.correct)
        self.assertFalse(bundle.isexposed("mysql"))

        # is exposed
        self.assertTrue(bundle.isexposed("wordpress"))

    def test_setservicename(self):
        # unknown service change requested
        bundle = BundleParser(self.correct)
        self.assertRaises(BundleError, bundle.setservicename, "fake", "even_more")

        # test name correctly changed
        bundle.setservicename("mysql", "database")
        # check service exists
        self.assertIsNotNone(bundle.getservice("database"))
        # check relation changed and : not affected
        # check :
        found = [True for relation in bundle.getrelations() if "database:db" in relation]
        self.assertTrue(found)
        # check without :
        found = [True for relation in bundle.getrelations() if "database" in relation]
        self.assertTrue(found)