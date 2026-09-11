from copy import deepcopy


class MemoryJobs:
    def __init__(self, status):
        self.jobs = {"job-1": {"id": "job-1", "status": status}}
        self.save_count = 0

    def get(self, job_id):
        return deepcopy(self.jobs[job_id])

    def save(self, job):
        self.save_count += 1
        self.jobs[job["id"]] = deepcopy(job)
