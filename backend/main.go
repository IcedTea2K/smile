package main

import (
	"crypto/tls"
	"fmt"
	"log"
	"net/http"
)

const (
	port         = ":8080"
	responseBody = "Hello, TLS!"
)

func main() {
	println("Listening on https://localhost:8080/")

	cert, err := tls.LoadX509KeyPair("certificates/localhost+2.pem", "certificates/localhost+2-key.pem")
	if err != nil {
		log.Fatalf("Failed to load X509 key pair: %v", err)
	}

	config := &tls.Config{
		Certificates: []tls.Certificate{cert},
		// MinVersion:   tls.VersionTLS12,
	}

	router := http.NewServeMux()
	router.HandleFunc("/", handleRequest)
	//http.HandleFunc("/smile", handleRequest)
	server := &http.Server{
		Addr:      port,
		Handler:   router,
		TLSConfig: config,
	}
	// log.Printf("Listening on %s...", port)
	err = server.ListenAndServeTLS("", "")
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

// this enables the CORS , change * to http address of front end
func enableCors(w *http.ResponseWriter) {
	fmt.Println("Enabling CORS")
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
}

// handle...later adjust this to what we need.
func handleRequest(w http.ResponseWriter, r *http.Request) {
	enableCors(&w)
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(responseBody))
}
