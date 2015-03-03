import os
import server
import unittest
import tempfile
from flask import json, jsonify
from src.config_parser import get_config
from src.s3_manager import S3Manager
from tests.test_context import TestContext

class FlaskrTestCase(TestContext):

	def setUp(self):
		server.app.config['TESTING'] = True
		self.app = server.app.test_client()

	def test_getting_mp4(self):
		response = self.app.get('/convert?url=http://media.giphy.com/media/WSqcqvTxgwfYs/giphy.gif')
		self.assertEqual(response.status_code, 200)

		data = json.loads(response.data)
		self.assertRegexpMatches(data['mp4'], 'https://s3.amazonaws.com/fusion-gif2html5-mp4')
		self.assertRegexpMatches(data['snapshot'], 'https://s3.amazonaws.com/fusion-gif2html5-mp4')

		file_to_delete = data['mp4'].split('/')[-1]

		s3Manager = S3Manager(get_config())
		s3Manager.delete(file_to_delete)



if __name__ == '__main__':
    unittest.main()