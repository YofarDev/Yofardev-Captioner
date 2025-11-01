package app

import (
    "fmt"
    "log"
    
    "github.com/yofardev/captioner/internal/config"
    "github.com/yofardev/captioner/internal/ui"
)

type App struct {
    config *config.Config
    uiApp  *ui.App
}

func New(cfg *config.Config) *App {
    return &App{
        config: cfg,
    }
}

func (a *App) Run() error {
    log.Println("Starting Yofardev Captioner Go application...")
    
    // Initialize UI
    a.uiApp = ui.NewApp(a.config)
    
    // Run UI
    if err := a.uiApp.Run(); err != nil {
        return fmt.Errorf("UI application error: %w", err)
    }
    
    log.Println("Yofardev Captioner Go application stopped.")
    return nil
}
