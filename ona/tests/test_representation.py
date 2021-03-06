import pytz
import unittest

from datetime import datetime

from ona.representation import OnaItemBase, PackageScanFormSubmission


SUBMITTED_AT_FORMAT = '%Y-%m-%dT%H:%M:%S'

SUBMISSION_JSON = {
    'gps': '24.24 25.25 1.0 5.0',
    'qr_code': 'asdf',
    '_submission_time': datetime.now().strftime(SUBMITTED_AT_FORMAT),
}


class TestOnaItem(unittest.TestCase):

    def test_not_a_dict(self):
        """Ona items must be instantiated with a dictionary."""
        with self.assertRaises(ValueError):
            OnaItemBase([])

    def test_normal_attribute(self):
        """Normal attributes should be accessible from the model."""
        item = OnaItemBase({})
        self.assertEqual(item.json, {})

    def test_dictionary_key(self):
        """JSON dictionary keys should be accessible from the model."""
        item = OnaItemBase({'hello': 'world'})
        self.assertEqual(item.hello, 'world')

    def test_test_precedence(self):
        """Normal attribute takes precedence over JSON dictionary key."""
        item = OnaItemBase({'json': 'hello'})
        self.assertEqual(item.json, {'json': 'hello'})

    def test_date_field(self):
        """If attr name is listed in _date_field_names, it should be cast as a date."""
        class TestItem(OnaItemBase):
            _date_attrs = ['hello']

        now = datetime.now().replace(microsecond=0).replace(tzinfo=pytz.UTC)
        item = TestItem({'hello': now.strftime(OnaItemBase._date_format)})
        self.assertEqual(item.hello, now)


class ProductTestCase(unittest.TestCase):
    """Basic test for Product object."""

    def setUp(self):
        self.form_submission = PackageScanFormSubmission(SUBMISSION_JSON)

    def test_qr_code(self):
        self.assertEqual(SUBMISSION_JSON['qr_code'], self.form_submission.qr_code)

    def test_gps(self):
        self.assertEqual(SUBMISSION_JSON['gps'], self.form_submission.gps)

    def test_no_gps(self):
        data = SUBMISSION_JSON.copy()
        data.pop('gps')
        self.form_submission = PackageScanFormSubmission(data)
        self.assertFalse(hasattr(self.form_submission, 'gps'))

    def test_submission_time(self):
        self.assertEqual(
            SUBMISSION_JSON['_submission_time'],
            self.form_submission._submission_time.strftime(SUBMITTED_AT_FORMAT))

    def test_get_latitude(self):
        value = float(SUBMISSION_JSON['gps'].split(' ')[0])
        self.assertEqual(value, self.form_submission.get_lat())

    def test_get_latitude_no_gps(self):
        data = SUBMISSION_JSON.copy()
        data.pop('gps')
        self.form_submission = PackageScanFormSubmission(data)
        self.assertIsNone(self.form_submission.get_lat())

    def test_get_longitude(self):
        value = float(SUBMISSION_JSON['gps'].split(' ')[1])
        self.assertEqual(value, self.form_submission.get_lng())

    def test_get_altitude(self):
        value = float(SUBMISSION_JSON['gps'].split(' ')[2])
        self.assertEqual(value, self.form_submission.get_altitude())

    def test_get_accuracy(self):
        value = float(SUBMISSION_JSON['gps'].split(' ')[3])
        self.assertEqual(value, self.form_submission.get_accuracy())

    def test_get_gps_data_out_of_range(self):
        self.assertIsNone(self.form_submission.get_gps_data(100))
