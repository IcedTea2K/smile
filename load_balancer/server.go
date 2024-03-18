package main
import "net/url"
// Defining a server type that the load balancer is manager

type Server struct {
    url url.URL
}

// health check -> number of connections
// serve proxy
