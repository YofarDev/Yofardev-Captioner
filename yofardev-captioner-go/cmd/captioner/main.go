package main

import (
    "flag"
    "log"
    
    "github.com/yofardev/captioner/internal/app"
    "github.com/yofardev/captioner/internal/config"
)

func main() {
    // Parse command-line flags
    configPath := flag.String("config", "", "path to config file")
    flag.Parse()
    
    // Load configuration
    cfg, err := config.Load(*configPath)
    if err != nil {
        log.Fatalf("Failed to load config: %v", err)
    }
    
    // Initialize and run application
    application := app.New(cfg)
    if err := application.Run(); err != nil {
        log.Fatalf("Application error: %v", err)
    }
}
