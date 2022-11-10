import sys
sys.path.append('../ChitChat')

from TaggedQueue import *


def test_put_request() -> None:
    q = TaggedQueue()
    j = Job('test', 'test')
    tag = q.put_request(j)
    assert q.request_queue[0].job_tag == tag


def test_put_response() -> None:
    q = TaggedQueue()
    j = Job('test', 'test')
    tag = q.put_request(j)
    r = Response(tag, 'test')
    q.put_response(tag, r)
    assert q.responses[tag].job_tag == r.job_tag


def test_wait_for_result() -> Response:
    q = TaggedQueue()
    j = Job('test', 'test')
    tag = q.put_request(j)
    r = Response(tag, 'test')
    q.put_response(tag, r)
    assert q.wait_for_result(tag).job_tag == r.job_tag


def test_next() -> None:
    q = TaggedQueue()
    j = Job('test', 'test')
    tag = q.put_request(j)
    r = Response(tag, 'test')
    q.put_response(tag, r)
    assert q.next().job_tag == j.job_tag