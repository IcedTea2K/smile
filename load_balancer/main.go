package main

import (
	"crypto/tls"
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"strconv"
)

const SERVER_URL = "https://server"
const SERVER_PORT = ":8080"
const SERVER_END_POINT = "/"

const PROXY_PORT = ":8000"

var   CURR_SERVER = 1

func main()  {
    // fmt.Println("Load balancing again yummy") 
    // http.HandleFunc("/{id}", serverRedirect)
    // http.HandleFunc("/", home)
    // log.Fatal(http.ListenAndServe(":8000", nil))

	cert, err := tls.LoadX509KeyPair(os.Getenv("SSL_CRT"), os.Getenv("SSL_KEY"))
	if err != nil {
		log.Fatalf("Failed to load X509 key pair: %v", err)
	}

	config := &tls.Config{
		Certificates: []tls.Certificate{cert},
		// MinVersion:   tls.VersionTLS12,
	}

	router := http.NewServeMux()
    router.HandleFunc("/", load_balance)
	// router.HandleFunc("/home", home)
	// router.HandleFunc("/{id}", serverRedirect)
	//http.HandleFunc("/smile", handleRequest)
	server := &http.Server{
		Addr:      PROXY_PORT,
		Handler:   router,
		TLSConfig: config,
	}
	// log.Printf("Listening on %s...", port)
	err = server.ListenAndServeTLS("", "")
	if err != nil {
		log.Fatalf("Failed to start server: %v", err)
	}
}

func load_balance(w http.ResponseWriter, r *http.Request) {
    serverPath, err := url.Parse(SERVER_URL + strconv.Itoa(CURR_SERVER) + SERVER_PORT)
    log.Println(serverPath.String())
    if err != nil {
        w.WriteHeader(http.StatusInternalServerError)
        w.Write([]byte("Fatal internal problems"))
        return
    }

    proxy := httputil.NewSingleHostReverseProxy(serverPath) 

    proxy.ServeHTTP(w, r)

    CURR_SERVER++
    if CURR_SERVER > 3 {
        CURR_SERVER = 1
    }
}

func serverRedirect(w http.ResponseWriter, r *http.Request) {
    if _, err := strconv.Atoi(r.PathValue("id")); r.PathValue("id") == "" || err != nil {
        fmt.Println("Tryingn to access an invalid server")
        w.WriteHeader(http.StatusNotFound)
        w.Write([]byte("Not a valid server"))
        return
    }

    serverPath, err := url.Parse(SERVER_URL + r.PathValue("id") + SERVER_PORT)
    log.Println(serverPath.String())
    if err != nil {
        w.WriteHeader(http.StatusInternalServerError)
        w.Write([]byte("Fatal internal problems"))
        return
    }

    proxy := httputil.NewSingleHostReverseProxy(serverPath) 
    r.URL.Path = SERVER_END_POINT

    proxy.ServeHTTP(w, r)
}
