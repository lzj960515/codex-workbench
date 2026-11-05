def cancel_export(repository, job_id):
    job = repository.get(job_id)
    if job["status"] != "pending":
        raise ValueError("job cannot be cancelled")
    job["status"] = "cancelled"
    repository.save(job)
    return job
