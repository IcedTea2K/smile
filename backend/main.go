package main

import (
	"fmt"
	// "log"
	"encoding/json"
	"net/http"
)

type Article struct {
	Id      string
	Title   string
	Desc    string
	Content string
}

var Articles []Article

func main() {
	println("Listening on http://localhost:8002/articles")
	Articles = []Article{
		{Id: "1", Title: "First article", Desc: "Title of this fine article", Content: "Content for this fine article"},
		{Id: "2", Title: "Second article", Desc: "Title of this majestic article", Content: "Content for this majestic article"},
	}
	http.HandleFunc("/articles", handleArticles)
	http.ListenAndServe(":8002", nil)
}

// func foo(w http.ResponseWriter, r *http.Request) {

// 	js, err := json.Marshal(Articles)
// 	if err != nil {
// 		http.Error(w, err.Error(), http.StatusInternalServerError)
// 		return
// 	}

// 	w.Header().Set("Content-Type", "application/json")
// 	w.Write(js)
// }

func enableCors(w *http.ResponseWriter) {
	fmt.Println("Enabling CORS")
	(*w).Header().Set("Access-Control-Allow-Origin", "http://localhost:3000")
}

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
