import io
import json
import unittest
from urllib.error import HTTPError, URLError
from client import NoRedirect, PopNowClient, PopNowError, approved_amount, input_object

KEY = 'sk-popnow-unit-test-not-a-credential'
class Response(io.BytesIO):
    pass
class Opener:
    def __init__(self, data=None, error=None):
        self.data = {'code': 200, 'data': data}
        self.error = error
        self.calls = []
    def open(self, request, timeout):
        self.calls.append((request, timeout))
        if self.error: raise self.error
        return Response(json.dumps(self.data).encode())

class ClientTests(unittest.TestCase):
    def test_quote_never_starts_task(self):
        opener = Opener({'quoteId':'q1','maxChargeUsd':'0.012345678'})
        result = PopNowClient(KEY, opener).invoke('quote', {'model':'vendor/model/text-to-image','input_json':'{"prompt":"a paper city"}'})
        req, timeout = opener.calls[0]
        self.assertTrue(req.full_url.endswith('/jobs/quote'))
        self.assertEqual(timeout, 60)
        self.assertEqual(json.loads(req.data), {'model':'vendor/model/text-to-image','input':{'prompt':'a paper city'}})
        self.assertEqual(result['maxChargeUsd'], '0.012345678')
        self.assertIsNone(req.get_header('Idempotency-key'))

    def test_create_exact_money_and_same_idempotency(self):
        opener = Opener({'taskId':'t1'})
        client = PopNowClient(KEY, opener)
        params = {'model':'vendor/model/task','input_json':'{"prompt":"hello"}','quote_id':'q1','approved_max_usd':'0.012345678','idempotency_key':'approved-task-001'}
        client.invoke('create', params)
        client.invoke('create', params)
        a, b = [x[0] for x in opener.calls]
        self.assertEqual(a.data, b.data)
        self.assertEqual(a.get_header('Idempotency-key'), b.get_header('Idempotency-key'))
        self.assertEqual(json.loads(a.data)['expectedCostUsd'], '0.012345678')
        self.assertEqual(json.loads(a.data)['quoteId'], 'q1')

    def test_approval_fields_required_before_network(self):
        opener=Opener()
        valid={'model':'vendor/model/task','input_json':'{}','quote_id':'q1','approved_max_usd':'0','idempotency_key':'id1'}
        for field in ('quote_id','approved_max_usd','idempotency_key'):
            params={k:v for k,v in valid.items() if k!=field}
            with self.assertRaises(PopNowError):PopNowClient(KEY,opener).invoke('create',params)
        self.assertEqual(opener.calls, [])

    def test_decimal_strings_only(self):
        for bad in (0,0.1,-1,'-1','NaN','Infinity','1e-3','0.1234567890',' 1','01','1.' ):
            with self.assertRaises(PopNowError):approved_amount(bad)
        self.assertEqual(approved_amount('0.000000001'), '0.000000001')
        self.assertEqual(approved_amount('0'), '0')

    def test_input_must_be_finite_json_object(self):
        for bad in ('[]','null','{"x":NaN}','{"x":1e999}','{"x":Infinity}','invalid'):
            with self.assertRaises(PopNowError):input_object(bad)
        self.assertEqual(input_object('{"nested":[1,2.5]}'), {'nested':[1,2.5]})

    def test_reference_url_is_only_payload(self):
        opener=Opener()
        PopNowClient(KEY,opener).invoke('quote', {'model':'vendor/image/task','input_json':'{"image_url":"https://example.org/reference.png"}'})
        self.assertEqual(len(opener.calls), 1)
        self.assertTrue(opener.calls[0][0].full_url.startswith('https://api.popnow.ai/api/v1/'))

    def test_safe_errors_omit_credentials_and_upstream_body(self):
        errors=[HTTPError('https://api.popnow.ai',401,KEY,{},io.BytesIO(KEY.encode())),URLError(KEY)]
        for error in errors:
            with self.assertRaises(PopNowError) as caught:PopNowClient(KEY,Opener(error=error)).invoke('balance',{})
            self.assertNotIn(KEY,str(caught.exception))

    def test_redirect_is_rejected(self):
        self.assertIsNone(NoRedirect().redirect_request(None,None,302,'redirect',{},'https://example.org'))

    def test_read_only_paths_and_encoded_query(self):
        opener=Opener()
        client=PopNowClient(KEY,opener)
        client.invoke('models',{'search':'image&x=secret'})
        client.invoke('balance',{})
        client.invoke('status',{'task_id':'t1&other=x'})
        for req,_ in opener.calls:self.assertEqual(req.get_method(),'GET')
        self.assertIn('search=image%26x%3Dsecret',opener.calls[0][0].full_url)
        self.assertIn('taskId=t1%26other%3Dx',opener.calls[2][0].full_url)
        with self.assertRaises(PopNowError):client.request('https://example.org')

    def test_idempotency_header_cannot_inject(self):
        opener=Opener()
        with self.assertRaises(PopNowError):PopNowClient(KEY,opener).request('/jobs/createTask',body={},idempotency_key='key\r\nx: y')
        self.assertEqual(opener.calls,[])

if __name__ == '__main__':unittest.main()
