package imageutil

import (
    "fmt"
    "image"
    "sync"
    
    "fyne.io/fyne/v2"
)

const (
    ThumbnailWidth  = 128
    ThumbnailHeight = 128
)

var (
    thumbnailCache = make(map[string]image.Image)
    cacheMutex     sync.Mutex
)

// GenerateThumbnail generates a thumbnail for the given image path.
// It uses a cache to avoid regenerating thumbnails for the same image.
func GenerateThumbnail(imagePath string) (image.Image, error) {
    cacheMutex.Lock()
    if thumb, ok := thumbnailCache[imagePath]; ok {
        cacheMutex.Unlock()
        return thumb, nil
    }
    cacheMutex.Unlock()
    
    img, err := Load(imagePath)
    if err != nil {
        return nil, err
    }
    
    thumb := Resize(img, ThumbnailWidth, ThumbnailHeight)
    
    cacheMutex.Lock()
    thumbnailCache[imagePath] = thumb
    cacheMutex.Unlock()
    
    return thumb, nil
}

// ClearThumbnailCache clears the entire thumbnail cache.
func ClearThumbnailCache() {
    cacheMutex.Lock()
    defer cacheMutex.Unlock()
    thumbnailCache = make(map[string]image.Image)
}

// ClearThumbnailCacheForPath removes a specific image's thumbnail from the cache.
func ClearThumbnailCacheForPath(imagePath string) {
    cacheMutex.Lock()
    defer cacheMutex.Unlock()
    delete(thumbnailCache, imagePath)
}

// GetThumbnailCacheSize returns the number of items currently in the thumbnail cache.
func GetThumbnailCacheSize() int {
    cacheMutex.Lock()
    defer cacheMutex.Unlock()
    return len(thumbnailCache)
}

// LoadThumbnail loads and generates a thumbnail as a Fyne resource
func LoadThumbnail(imagePath string, width, height int) (*fyne.StaticResource, error) {
    _, err := GenerateThumbnail(imagePath)
    if err != nil {
        return nil, err
    }
    
    // Convert image to Fyne resource
    // For now, we'll return a placeholder
    // TODO: Implement proper image to Fyne resource conversion
    return nil, fmt.Errorf("LoadThumbnail not fully implemented yet")
}
