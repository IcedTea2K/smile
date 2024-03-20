# S.M.I.L.E
## How to Run the Project
Currently, only the back-end and load-balancer is contained within Docker. Though, for the https protocol to work, certificates must be genereted and stored in trusted place. Run the following command to generate certificates, and copy the rootCA certificate to the project directory (all automatic)
```sh
smile
➜ ./gen-cert.sh
```
Next, run
```sh
smile
➜ docker compose up
```
and the cluster of servers will be up with 3 different servers and a load-balancer. Now you could go to `https://localhost:8000` to test out cutting-edge load balancing capabilities.

Instructions on ML TBD

## How it works
### Load balancing algorithm
The loadbalancer is currently the only one exposed to the public. It's the gateway to access the three servers. The implemented algorithm is dead simple. It is a round-robin, where each server takes turn processing the request. On theory, the workload will be divided evenly among the servers. Although, not all requests have the same workload, so some server might end up doing more work than the other. Additionally, if one server is down, there is no high-availability capabilities, to transfer ongoing requests to healthy servers. As such, better algorithm will be needed, and the load-balancer needs to be able to monitor the health of the servers.
