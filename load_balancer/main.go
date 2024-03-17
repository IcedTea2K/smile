package main

import (
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
)

const SERVER_URL = "http://server"
const SERVER_PORT = ":8080"
const SERVER_END_POINT = "/smile"

func main()  {
    fmt.Println("Load balancing again") 
    http.HandleFunc("/{id}", serverRedirect)
    http.HandleFunc("/", home)
    log.Fatal(http.ListenAndServe(":8000", nil))
}

type Message struct {
    Name string
    Content string
    Server string
}

func home(w http.ResponseWriter, r *http.Request) {
    fmt.Println("At home with rey")
}

func serverRedirect(w http.ResponseWriter, r *http.Request) {
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
