package services

import (
    "fmt"
    "image"
    "io/fs"
    "os"
    "path/filepath"
    "sort"
    "strings"
    "sync"
    
    "fyne.io/fyne/v2"
    "github.com/yofardev/captioner/pkg/imageutil"
)

type ImageService struct {
    mu sync.Mutex
}

func NewImageService() *ImageService {
    return &ImageService{}
}

// ListImagesInFolder lists all supported image files in a given folder.
func (s *ImageService) ListImagesInFolder(folderPath string) ([]string, error) {
    var imagePaths []string
    
    err := filepath.WalkDir(folderPath, func(path string, d fs.DirEntry, err error) error {
        if err != nil {
            return err
        }
        if !d.IsDir() && s.isSupportedImage(path) {
            imagePaths = append(imagePaths, path)
        }
        return nil
    })
    
    if err != nil {
        return nil, fmt.Errorf("failed to walk directory: %w", err)
    }
    
    sort.Strings(imagePaths) // Sort for consistent order
    return imagePaths, nil
}

// isSupportedImage checks if a file has a supported image extension.
func (s *ImageService) isSupportedImage(filename string) bool {
    ext := strings.ToLower(filepath.Ext(filename))
    switch ext {
    case ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp":
        return true
    }
    return false
}

// RenameImage renames an image file and its associated caption file (if any).
func (s *ImageService) RenameImage(oldPath, newPath string) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    // Rename image file
    if err := os.Rename(oldPath, newPath); err != nil {
        return fmt.Errorf("failed to rename image file: %w", err)
    }
    
    // Rename caption file (assuming .txt extension)
    oldCaptionPath := strings.TrimSuffix(oldPath, filepath.Ext(oldPath)) + ".txt"
    newCaptionPath := strings.TrimSuffix(newPath, filepath.Ext(newPath)) + ".txt"
    
    if _, err := os.Stat(oldCaptionPath); err == nil { // Check if old caption file exists
        if err := os.Rename(oldCaptionPath, newCaptionPath); err != nil {
            // Log error but don't fail the whole operation if caption file rename fails
            fmt.Printf("Warning: Failed to rename caption file from %s to %s: %v\n", oldCaptionPath, newCaptionPath, err)
        }
    }
    
    // Clear thumbnail cache for old path
    imageutil.ClearThumbnailCacheForPath(oldPath)
    
    return nil
}

// DeleteImage deletes an image file and its associated caption file (if any).
func (s *ImageService) DeleteImage(imagePath string) error {
    s.mu.Lock()
    defer s.mu.Unlock()
    
    // Delete image file
    if err := os.Remove(imagePath); err != nil {
        return fmt.Errorf("failed to delete image file: %w", err)
    }
    
    // Delete caption file (assuming .txt extension)
    captionPath := strings.TrimSuffix(imagePath, filepath.Ext(imagePath)) + ".txt"
    if _, err := os.Stat(captionPath); err == nil { // Check if caption file exists
        if err := os.Remove(captionPath); err != nil {
            // Log error but don't fail the whole operation if caption file deletion fails
            fmt.Printf("Warning: Failed to delete caption file %s: %v\n", captionPath, err)
        }
    }
    
    // Clear thumbnail cache for the deleted path
    imageutil.ClearThumbnailCacheForPath(imagePath)
    
    return nil
}

// LoadImage loads an image from the given path
func (s *ImageService) LoadImage(imagePath string) (image.Image, error) {
    return imageutil.Load(imagePath)
}

// LoadImageThumbnail loads a thumbnail for the given image
func (s *ImageService) LoadImageThumbnail(imagePath string, size fyne.Size) (fyne.Resource, error) {
    return imageutil.LoadThumbnail(imagePath, int(size.Width), int(size.Height))
}
