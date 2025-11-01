package imageutil

import (
    "fmt"
    "image"
    "image/jpeg"
    "image/png"
    "os"
    "path/filepath"
    
    "golang.org/x/image/draw"
)

// Load loads an image from the given path.
func Load(imagePath string) (image.Image, error) {
    file, err := os.Open(imagePath)
    if err != nil {
        return nil, err
    }
    defer file.Close()
    
    img, _, err := image.Decode(file)
    if err != nil {
        return nil, err
    }
    return img, nil
}

// Resize resizes an image to the specified width and height.
func Resize(img image.Image, width, height int) image.Image {
    dst := image.NewRGBA(image.Rect(0, 0, width, height))
    draw.CatmullRom.Scale(dst, dst.Bounds(), img, img.Bounds(), draw.Src, nil)
    return dst
}

// Save saves an image to the specified path with the given format.
func Save(imagePath string, img image.Image) error {
    file, err := os.Create(imagePath)
    if err != nil {
        return err
    }
    defer file.Close()
    
    switch filepath.Ext(imagePath) {
    case ".jpg", ".jpeg":
        return jpeg.Encode(file, img, nil)
    case ".png":
        return png.Encode(file, img)
    default:
        return fmt.Errorf("unsupported image format: %s", filepath.Ext(imagePath))
    }
}
