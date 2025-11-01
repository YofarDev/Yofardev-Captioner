package services

import (
    "context"
    "fmt"
    
    "github.com/yofardev/captioner/internal/config"
    "github.com/yofardev/captioner/internal/storage"
)

type SessionService struct {
    storage storage.Storage
    config  *config.Config
}

func NewSessionService(cfg *config.Config) (*SessionService, error) {
    var s storage.Storage
    var err error
    
    switch cfg.Storage.Type {
    case "sqlite":
        s, err = storage.NewSQLiteStorage(cfg.Storage.Path)
        if err != nil {
            return nil, fmt.Errorf("failed to create SQLite storage: %w", err)
        }
    default:
        return nil, fmt.Errorf("unsupported storage type: %s", cfg.Storage.Type)
    }
    
    return &SessionService{
        storage: s,
        config:  cfg,
    }, nil
}

func (s *SessionService) Save(ctx context.Context, session *storage.Session) error {
    return s.storage.Save(ctx, session)
}

func (s *SessionService) Load(ctx context.Context) (*storage.Session, error) {
    return s.storage.Load(ctx)
}

func (s *SessionService) Close() error {
    return s.storage.Close()
}

// SaveCaption saves a caption for a specific image
func (s *SessionService) SaveCaption(ctx context.Context, imagePath, caption string) error {
    return s.storage.SaveCaption(ctx, imagePath, caption)
}

// LoadCaption loads a caption for a specific image
func (s *SessionService) LoadCaption(ctx context.Context, imagePath string) (string, error) {
    return s.storage.LoadCaption(ctx, imagePath)
}

// GetLastOpenedFolder returns the last opened folder path
func (s *SessionService) GetLastOpenedFolder() string {
    session, err := s.Load(context.Background())
    if err != nil {
        return ""
    }
    return session.CurrentFolder
}

// SetLastOpenedFolder sets the last opened folder path
func (s *SessionService) SetLastOpenedFolder(folderPath string) {
    session, err := s.Load(context.Background())
    if err != nil {
        session = &storage.Session{}
    }
    session.CurrentFolder = folderPath
    _ = s.Save(context.Background(), session)
}
