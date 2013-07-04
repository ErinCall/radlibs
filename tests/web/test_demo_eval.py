from __future__ import unicode_literals

import json
from nose.tools import eq_
from tests import TestCase

from nose.plugins.skip import SkipTest


class TestDemoEval(TestCase):
    def test_a_simple_eval(self):
        libs = {
            'Animal': ['cat'],
        }

        response = self.app.post('/demo_eval', data={
            'libs': json.dumps(libs),
            'rad': '<Animal>',
        })

        body = json.loads(response.data)
        eq_(body, {'status': 'ok', 'radlib': 'cat'})

    def test_reference_a_nonexistent_lib(self):
        response = self.app.post('/demo_eval', data={
            'libs': '{}',
            'rad': '<Yeezy>',
        })
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "No such Library 'Yeezy'"
            })

    def test_syntactically_invalid_rad(self):
        response = self.app.post('/demo_eval', data={
            'libs': '{}',
            'rad': '<Open',
        })
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "Rule 'contents' matched in its entirety, but it didn't "
                     "consume all the text. The non-matching portion of the "
                     "text begins with '<Open' (line 1, column 1)."
            })

    def test_missing_libs_param(self):
        response = self.app.post('/demo_eval', data={
            'rad': 'even with no libs referenced',
        })
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "the 'libs' param is required",
            })

    def test_libs_param_is_invalid_json(self):
        response = self.app.post('/demo_eval', data={
            'rad': 'foo',
            'libs': '{',
        })
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "'libs' param is not valid JSON: "
                     "Expecting object: line 1 column 0 (char 0)",
            })

    def test_missing_rad_param(self):
        response = self.app.post('/demo_eval', data={
            'libs': '{}'
        })
        eq_(response.status_code, 200, response.data)
        body = json.loads(response.data)
        eq_(body, {
            'status': 'error',
            'error': "the 'rad' param is required",
            })
