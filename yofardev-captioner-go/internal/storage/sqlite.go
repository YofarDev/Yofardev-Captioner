package storage

import (
    "context"
    "database/sql"
    "encoding/json"
    "fmt"
    "os"
    "path/filepath"
    
    _ "github.com/mattn/go-sqlite3"
)

type SQLiteStorage struct {
    db   *sql.DB
    path string
}

func NewSQLiteStorage(path string) (*SQLiteStorage, error) {
    dir := filepath.Dir(path)
    if err := os.MkdirAll(dir, 0755); err != nil {
        return nil, fmt.Errorf("failed to create storage directory: %w", err)
    }
    
    db, err := sql.Open("sqlite3", path)
    if err != nil {
        return nil, fmt.Errorf("failed to open database: %w", err)
    }
    
    storage := &SQLiteStorage{
        db:   db,
        path: path,
    }
    
    if err := storage.initSchema(); err != nil {
        storage.Close()
        return nil, fmt.Errorf("failed to initialize schema: %w", err)
    }
    
    return storage, nil
}

func (s *SQLiteStorage) initSchema() error {
    queries := []string{
        `CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL
        );`,
        `CREATE TABLE IF NOT EXISTS captions (
            image_path TEXT PRIMARY KEY,
            caption TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );`,
    }
    
    for _, query := range queries {
        if _, err := s.db.Exec(query); err != nil {
            return err
        }
    }
    return nil
}

func (s *SQLiteStorage) Save(ctx context.Context, session *Session) error {
    jsonData, err := json.Marshal(session)
    if err != nil {
        return fmt.Errorf("failed to marshal session: %w", err)
    }
    
    // Always update the single session entry (id=1)
    query := `
    INSERT OR REPLACE INTO sessions (id, data) VALUES (1, ?);
    `
    _, err = s.db.ExecContext(ctx, query, jsonData)
    if err != nil {
        return fmt.Errorf("failed to save session: %w", err)
    }
    return nil
}

func (s *SQLiteStorage) Load(ctx context.Context) (*Session, error) {
    query := `
    SELECT data FROM sessions WHERE id = 1;
    `
    row := s.db.QueryRowContext(ctx, query)
    
    var jsonData []byte
    err := row.Scan(&jsonData)
    if err == sql.ErrNoRows {
        return &Session{
            FileMap: make(map[string]string),
        }, nil // Return empty session if no data
    }
    if err != nil {
        return nil, fmt.Errorf("failed to load session: %w", err)
    }
    
    var session Session
    if err := json.Unmarshal(jsonData, &session); err != nil {
        return nil, fmt.Errorf("failed to unmarshal session: %w", err)
    }
    
    if session.FileMap == nil {
        session.FileMap = make(map[string]string)
    }
    
    return &session, nil
}

func (s *SQLiteStorage) SaveCaption(ctx context.Context, imagePath, caption string) error {
    query := `
    INSERT OR REPLACE INTO captions (image_path, caption, updated_at)
    VALUES (?, ?, CURRENT_TIMESTAMP);
    `
    _, err := s.db.ExecContext(ctx, query, imagePath, caption)
    if err != nil {
        return fmt.Errorf("failed to save caption: %w", err)
    }
    return nil
}

func (s *SQLiteStorage) LoadCaption(ctx context.Context, imagePath string) (string, error) {
    query := `
    SELECT caption FROM captions WHERE image_path = ?;
    `
    row := s.db.QueryRowContext(ctx, query, imagePath)
    
    var caption string
    err := row.Scan(&caption)
    if err == sql.ErrNoRows {
        return "", fmt.Errorf("no caption found for image: %s", imagePath)
    }
    if err != nil {
        return "", fmt.Errorf("failed to load caption: %w", err)
    }
    
    return caption, nil
}

func (s *SQLiteStorage) Close() error {
    return s.db.Close()
}
