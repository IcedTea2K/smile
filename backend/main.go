package main

import (
	"fmt"
	// "log"
	"encoding/json"
	"net/http"
)

// probs delete
type Article struct {
	Id      string
	Title   string
	Desc    string
	Content string
}

var Articles []Article

func main() {
	println("Listening on http://localhost:8080/smile")

	//probs change rah
	Articles = []Article{
		{Id: "1", Title: "First article", Desc: "Title of this fine article", Content: "Content for this fine article"},
		{Id: "2", Title: "Second article", Desc: "Title of this majestic article", Content: "Content for this majestic article"},
	}
	http.HandleFunc("/smile", handleArticles)
	http.ListenAndServe(":8080", nil)
}

// don't change this, this enables the CORS , change * to http address of front end
func enableCors(w *http.ResponseWriter) {
	fmt.Println("Enabling CORS")
	(*w).Header().Set("Access-Control-Allow-Origin", "*")
}

// handle...later adjust this to what we need.
func handleArticles(w http.ResponseWriter, r *http.Request) {

	enableCors(&w)
	js, err := json.Marshal(Articles)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	w.Write(js)
}
