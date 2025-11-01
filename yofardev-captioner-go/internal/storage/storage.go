package storage

import "context"

// Session represents the application's persistent state
type Session struct {
    CurrentFolder string
    CurrentImage  string
    FileMap       map[string]string
    SelectedModel string
    PromptText    string
}

// Storage defines the interface for persisting and loading application sessions
type Storage interface {
    Save(ctx context.Context, session *Session) error
    Load(ctx context.Context) (*Session, error)
    SaveCaption(ctx context.Context, imagePath, caption string) error
    LoadCaption(ctx context.Context, imagePath string) (string, error)
    Close() error
}
