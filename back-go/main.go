package main

import (
	"log"
	"nareshka-backend/app"
)

func main() {
	app, err := app.NewApp()
	if err != nil {
		log.Fatal("Failed to initialize app:", err)
	}

	if err := app.Run(); err != nil {
		log.Fatal("Failed to run app:", err)
	}
}