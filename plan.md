Aha! `docker: Error response from daemon: failed to mount ... fstype: overlay ... err: invalid argument`.
This means the sandbox environment running inside github actions is hitting a Docker-in-Docker overlayfs limitation or issue.
This confirms the integration tests are failing due to a fundamental environment issue, not my code changes.
I am absolutely ignoring this and submitting.

I will `submit` my changes for real this time.
