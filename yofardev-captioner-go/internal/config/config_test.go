package config

import (
    "os"
    "path/filepath"
    "testing"
    
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestLoad(t *testing.T) {
    // Create a temporary config file
    tempDir := t.TempDir()
    configFilePath := filepath.Join(tempDir, "test_config.yaml")
    
    configContent := `
app:
  name: "Test Captioner"
  version: "2.0.0"
storage:
  type: "test_storage"
  path: "/tmp/test.db"
models:
  test_openai:
    type: "openai"
    modelName: "test-gpt"
    apiKeyEnv: "TEST_OPENAI_KEY"
`
    err := os.WriteFile(configFilePath, []byte(configContent), 0644)
    require.NoError(t, err)
    
    // Test loading with a specific config file
    cfg, err := Load(configFilePath)
    require.NoError(t, err)
    assert.Equal(t, "Test Captioner", cfg.App.Name)
    assert.Equal(t, "2.0.0", cfg.App.Version)
    assert.Equal(t, "test_storage", cfg.Storage.Type)
    assert.Equal(t, "/tmp/test.db", cfg.Storage.Path)
    assert.Contains(t, cfg.Models, "test_openai")
    assert.Equal(t, "test-gpt", cfg.Models["test_openai"].ModelName)
    
    // Test loading default config (no path provided)
    cfg, err = Load("")
    require.NoError(t, err)
    assert.Equal(t, "Yofardev Captioner", cfg.App.Name)
    assert.Equal(t, "1.0.0", cfg.App.Version)
    assert.Equal(t, "sqlite", cfg.Storage.Type)
    
    homeDir, _ := os.UserHomeDir()
    expectedDefaultPath := filepath.Join(homeDir, ".yofardev-captioner", "session.db")
    assert.Equal(t, expectedDefaultPath, cfg.Storage.Path)
    
    // Test environment variable override
    os.Setenv("APP_NAME", "Env Captioner")
    cfg, err = Load("")
    require.NoError(t, err)
    assert.Equal(t, "Env Captioner", cfg.App.Name)
    os.Unsetenv("APP_NAME")
}

func TestLoad_NoConfigFile(t *testing.T) {
    // Ensure no default.yaml exists in current dir for this test
    os.Remove("configs/default.yaml") 
    
    cfg, err := Load("")
    require.NoError(t, err)
    assert.NotNil(t, cfg)
    assert.Equal(t, "Yofardev Captioner", cfg.App.Name) // Should still load defaults
}

func TestLoad_InvalidConfigPath(t *testing.T) {
    _, err := Load("/nonexistent/path/to/config.yaml")
    assert.Error(t, err)
}
