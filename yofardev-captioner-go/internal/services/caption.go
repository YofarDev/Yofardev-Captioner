package services

import (
    "context"
    "fmt"
    "sync"
    
    "github.com/yofardev/captioner/internal/models"
)

type CaptionService struct {
    registry    *models.Registry
    mu          sync.RWMutex
    inProgress  map[string]context.CancelFunc
}

func NewCaptionService(registry *models.Registry) *CaptionService {
    return &CaptionService{
        registry:   registry,
        inProgress: make(map[string]context.CancelFunc),
    }
}

type CaptionResult struct {
    ImagePath string
    Caption   string
    Error     error
}

func (s *CaptionService) GenerateCaption(ctx context.Context, modelName, imagePath, prompt string) (string, error) {
    model, err := s.registry.Get(modelName)
    if err != nil {
        return "", fmt.Errorf("model not found: %w", err)
    }
    
    if !model.IsAvailable() {
        return "", fmt.Errorf("model %s is not available", modelName)
    }
    
    return model.GenerateCaption(ctx, imagePath, prompt)
}

func (s *CaptionService) GenerateCaptionAsync(modelName, imagePath, prompt string) <-chan CaptionResult {
    resultCh := make(chan CaptionResult, 1)
    
    ctx, cancel := context.WithCancel(context.Background())
    
    s.mu.Lock()
    s.inProgress[imagePath] = cancel
    s.mu.Unlock()
    
    go func() {
        defer func() {
            s.mu.Lock()
            delete(s.inProgress, imagePath)
            s.mu.Unlock()
            close(resultCh)
        }()
        
        caption, err := s.GenerateCaption(ctx, modelName, imagePath, prompt)
        resultCh <- CaptionResult{
            ImagePath: imagePath,
            Caption:   caption,
            Error:     err,
        }
    }()
    
    return resultCh
}

func (s *CaptionService) GenerateBatch(ctx context.Context, modelName string, images []string, prompt string) <-chan CaptionResult {
    resultCh := make(chan CaptionResult, len(images))
    
    var wg sync.WaitGroup
    
    for _, imagePath := range images {
        wg.Add(1)
        go func(path string) {
            defer wg.Done()
            
            caption, err := s.GenerateCaption(ctx, modelName, path, prompt)
            resultCh <- CaptionResult{
                ImagePath: path,
                Caption:   caption,
                Error:     err,
            }
        }(imagePath)
    }
    
    go func() {
        wg.Wait()
        close(resultCh)
    }()
    
    return resultCh
}

func (s *CaptionService) Cancel(imagePath string) {
    s.mu.RLock()
    cancel, exists := s.inProgress[imagePath]
    s.mu.RUnlock()
    
    if exists {
        cancel()
    }
}

func (s *CaptionService) CancelAll() {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    for _, cancel := range s.inProgress {
        cancel()
    }
    s.inProgress = make(map[string]context.CancelFunc)
}

// ListModels returns a list of all registered model names.
func (s *CaptionService) ListModels() []string {
    return s.registry.List()
}
