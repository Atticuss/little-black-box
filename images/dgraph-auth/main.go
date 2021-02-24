// modified from the example here:
// https://rogerwelin.github.io/traefik/api/go/auth/2019/08/19/build-external-api-with-trafik-go.html

package main

import (
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

type config struct {
	AuthSecret string
}

func (conf *config) authHandler(w http.ResponseWriter, r *http.Request) {
	authToken := r.Header.Get("Authorization")

	if authToken == "" {
		w.WriteHeader(401)
		io.WriteString(w, `{"error": "missing Authorization header"}`)
		return
	}

	if authToken != conf.AuthSecret {
		w.WriteHeader(401)
		io.WriteString(w, `{"error": "incorrect Authorization header value"}`)
		return
	}

	w.WriteHeader(200)
	io.WriteString(w, `{"error": ""}`)
}

func main() {
	val, ok := os.LookupEnv("AUTH_SECRET")
	if !ok {
		log.Fatal("could not find expected env var: AUTH_SECRET")
	}

	c := config{AuthSecret: val}
	addr := "0.0.0.0:5000"

	router := http.NewServeMux()
	router.HandleFunc("/auth", c.authHandler)

	srv := &http.Server{
		Addr:         addr,
		WriteTimeout: time.Second * 5,
		ReadTimeout:  time.Second * 5,
		Handler:      router,
	}
	log.Fatal(srv.ListenAndServe())
}
