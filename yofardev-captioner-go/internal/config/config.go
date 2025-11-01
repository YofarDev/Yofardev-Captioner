package config

import (
    "fmt"
    "os"
    "path/filepath"
    
    "github.com/spf13/viper"
)

type Config struct {
    App struct {
        Name    string
        Version string
    }
    APIKeys map[string]string
    Storage struct {
        Type string
        Path string
    }
    Models map[string]ModelConfig
}

type ModelConfig struct {
    Type      string
    BaseURL   string
    ModelName string
    APIKeyEnv string
}

func Load(configPath string) (*Config, error) {
    v := viper.New()
    v.SetConfigName("default")
    v.SetConfigType("yaml")
    v.AddConfigPath("./configs") // Path to default config
    
    if configPath != "" {
        v.SetConfigFile(configPath)
    }
    
    // Read default config
    if err := v.ReadInConfig(); err != nil {
        if _, ok := err.(viper.ConfigFileNotFoundError); !ok {
            return nil, fmt.Errorf("failed to read default config: %w", err)
        }
    }
    
    // Read environment variables
    v.AutomaticEnv()
    
    var cfg Config
    if err := v.Unmarshal(&cfg); err != nil {
        return nil, fmt.Errorf("failed to unmarshal config: %w", err)
    }
    
    // Set default values if not present
    if cfg.App.Name == "" {
        cfg.App.Name = "Yofardev Captioner"
    }
    if cfg.App.Version == "" {
        cfg.App.Version = "1.0.0"
    }
    if cfg.Storage.Type == "" {
        cfg.Storage.Type = "sqlite"
    }
    if cfg.Storage.Path == "" {
        homeDir, err := os.UserHomeDir()
        if err != nil {
            return nil, fmt.Errorf("failed to get user home directory: %w", err)
        }
        cfg.Storage.Path = filepath.Join(homeDir, ".yofardev-captioner", "session.db")
    }
    
    return &cfg, nil
}
