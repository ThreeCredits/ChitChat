import time
from typing import *
import datetime

QUEUE_RESPONSE_TIMEOUT = 15
QUEUE_CHECK_DELAY = 0.1

class Job():
    """
    The Job class is used to store the jobs to be executed by the worker threads
    """

    def __init__(self, type: str, args: TypedDict, job_tag: int = None):
        """
        The constructor of the Job class
        """
        self.type = type
        self.args = args
        self.job_tag = job_tag
        self.request_time = None
        self.response_time = None


class Response():
    """
    The Response class is used to store the responses of the worker threads
    """

    def __init__(self, job_tag: int, result: Any):
        """
        The constructor of the Response class
        """
        self.job_tag = job_tag
        self.result = result
    
    def __getitem__(self, index):
        return self.result[index]


class TaggedQueue():
    """
    The tagged queue is responsible for storing the jobs to be executed by the worker threads.
    It is designed to be used by multiple threads, so it is thread-safe.
    It also provides methods
    """

    def __init__(self):
        """
        The constructor of the TaggedQueue class
        """
        # We store the queue
        self.request_queue = []
        self.responses = {}
        # We store the number of jobs
        self.number_of_jobs = 0

    def __len__(self):
        """
        The length of the queue
        """
        return len(self.queue)

    def put_request(self, job: Job):
        """
        Puts a job in the queue
        """
        # We increment the number of jobs
        self.number_of_jobs += 1
        # Generate a new job tag
        job_tag = self.number_of_jobs
        # assign the job tag to the job
        job.job_tag = job_tag
        # store the time of the request
        job.request_time = datetime.datetime.now()
        # We insert the job in the queue
        self.request_queue.append(job)
        # We return the job tag
        return job_tag

    def put_response(self, job_tag: int, response: Response):
        """
        Puts a response in the queue
        """
        # We store the response
        self.responses[job_tag] = response

    def wait_for_result(self, tag, timeout: int = QUEUE_RESPONSE_TIMEOUT, pop_response : bool = True) -> Response:
        """
        Waits for a result with the given tag
        """
        # We get the current time
        start_time = time.time()
        # We loop until we find the result
        while True:
            # We check if the timeout has been reached
            if time.time() - start_time > timeout:
                return None
            # We check if the result is in the queue
            if tag in self.responses:
                # We get the response
                response = self.responses[tag]
                # We check if we have to pop the response
                if pop_response:
                    # We pop the response
                    del self.responses[tag]
                # We return the response
                return response
            # We wait a bit
            time.sleep(0)

    def next(self):
        """
        Returns the next job in the queue
        """
        # We check if the queue is empty
        if len(self.request_queue) == 0:
            return None
        # We get the next job
        job = self.request_queue.pop(0)
        # We return the job
        return job