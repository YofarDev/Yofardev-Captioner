package imageutil

import (
    "bytes"
    "encoding/base64"
    "fmt"
    "image"
    "image/jpeg"
    "image/png"
    "os"
)

// ToDataURL encodes an image from the given path into a base64 data URL.
func ToDataURL(imagePath string) (string, error) {
    file, err := os.Open(imagePath)
    if err != nil {
        return "", fmt.Errorf("failed to open image file: %w", err)
    }
    defer file.Close()
    
    img, format, err := image.Decode(file)
    if err != nil {
        return "", fmt.Errorf("failed to decode image: %w", err)
    }
    
    var buf bytes.Buffer
    switch format {
    case "jpeg":
        err = jpeg.Encode(&buf, img, nil)
    case "png":
        err = png.Encode(&buf, img)
    default:
        return "", fmt.Errorf("unsupported image format for data URL: %s", format)
    }
    
    if err != nil {
        return "", fmt.Errorf("failed to encode image to buffer: %w", err)
    }
    
    return fmt.Sprintf("data:image/%s;base64,%s", format, base64.StdEncoding.EncodeToString(buf.Bytes())), nil
}
