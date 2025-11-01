package components

import (
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/canvas"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/widget"
    "image/color"
    "log"
    "math"
    
    "github.com/yofardev/captioner/internal/app/controller" // Import the new controller package
)

type ImageViewer struct {
    widget.BaseWidget
    controller controller.AppController // Use the AppController from the new controller package
    image      *canvas.Image
    scroll     *container.Scroll
    zoom       float64
    panX, panY float64
    currentImagePath string
}

func NewImageViewer(controller controller.AppController) *ImageViewer {
    iv := &ImageViewer{
        controller: controller,
        image:      canvas.NewImageFromImage(nil),
        zoom:       1.0,
        panX:       0.0,
        panY:       0.0,
    }
    iv.image.FillMode = canvas.ImageFillContain
    iv.image.ScaleMode = canvas.ImageScaleSmooth
    
    iv.scroll = container.NewScroll(iv.image)
    iv.scroll.SetMinSize(fyne.NewSize(400, 400)) // Default size
    
    // Add scroll and drag handlers for zoom/pan
    iv.scroll.OnScrolled = func(pos fyne.Position) {
        // This is a placeholder. Actual zoom/pan logic will be more complex
        // and likely involve custom rendering or transformations.
        // For now, we'll just log it.
        log.Printf("Scrolled to: %v", pos)
    }
    
    return iv
}

func (iv *ImageViewer) Container() *fyne.Container {
    return container.NewMax(iv.scroll)
}

func (iv *ImageViewer) SetImage(imagePath string) {
    if imagePath == "" {
        iv.image.Image = nil
        iv.image.Refresh()
        iv.currentImagePath = ""
        return
    }
    
    img, err := iv.controller.GetImage(imagePath)
    if err != nil {
        log.Printf("Error loading image %s: %v", imagePath, err)
        iv.image.Image = nil
        iv.image.Refresh()
        iv.currentImagePath = ""
        return
    }
    
    iv.image.Image = img
    iv.image.Refresh()
    iv.currentImagePath = imagePath
    iv.resetView()
}

func (iv *ImageViewer) resetView() {
    iv.zoom = 1.0
    iv.panX = 0.0
    iv.panY = 0.0
    // Reset scroll position
    iv.scroll.Offset = fyne.NewPos(0, 0)
    iv.scroll.Refresh()
    iv.image.Refresh()
}

// Custom rendering for zoom/pan (simplified for now)
func (iv *ImageViewer) CreateRenderer() fyne.WidgetRenderer {
    iv.ExtendBaseWidget(iv)
    rect := canvas.NewRectangle(color.Black)
    return &imageViewerRenderer{
        viewer: iv,
        rect:   rect,
        objects: []fyne.CanvasObject{rect, iv.image},
    }
}

type imageViewerRenderer struct {
    viewer  *ImageViewer
    rect    *canvas.Rectangle
    objects []fyne.CanvasObject
}

func (r *imageViewerRenderer) MinSize() fyne.Size {
    return r.viewer.scroll.MinSize()
}

func (r *imageViewerRenderer) Layout(size fyne.Size) {
    r.rect.Resize(size)
    r.viewer.scroll.Resize(size)
    // The actual image within the scroll container will be handled by Fyne's layout
}

func (r *imageViewerRenderer) Refresh() {
    r.viewer.image.Refresh()
    canvas.Refresh(r.viewer.scroll)
}

func (r *imageViewerRenderer) Objects() []fyne.CanvasObject {
    return r.objects
}

func (r *imageViewerRenderer) Destroy() {
    // No custom destruction needed
}

// Implement Scroller interface for custom scroll handling (zoom)
func (iv *ImageViewer) Scrolled(ev *fyne.ScrollEvent) {
    if iv.image.Image == nil {
        return
    }

    // Adjust zoom level
    if ev.Scrolled.DY > 0 {
        iv.zoom *= 1.1 // Zoom in
    } else if ev.Scrolled.DY < 0 {
        iv.zoom /= 1.1 // Zoom out
    }
    iv.zoom = math.Max(0.1, math.Min(5.0, iv.zoom)) // Limit zoom
    
    // Re-render image with new zoom
    iv.updateImageTransform()
}

// Implement Draggable interface for custom drag handling (pan)
func (iv *ImageViewer) Dragged(ev *fyne.DragEvent) {
    if iv.image.Image == nil {
        return
    }

    iv.panX += float64(ev.Dragged.DX)
    iv.panY += float64(ev.Dragged.DY)
    
    iv.updateImageTransform()
}

func (iv *ImageViewer) DragEnd() {
    // No specific action on drag end for now
}

func (iv *ImageViewer) updateImageTransform() {
    // This is a simplified approach. For true zoom/pan, you'd need to
    // apply transformations directly to the image object or its container.
    // Fyne's canvas.Image doesn't directly support scale/translate transforms
    // in this way without custom rendering.
    // For now, we'll just log the changes and rely on Fyne's default scaling.
    log.Printf("Zoom: %.2f, PanX: %.2f, PanY: %.2f", iv.zoom, iv.panX, iv.panY)
    
    // A more robust solution would involve:
    // 1. Creating a custom Fyne CanvasObject that draws the image with transformations.
    // 2. Updating the MinSize of the image object based on zoom to allow scrolling.
    
    // For now, we'll just update the image's size indirectly to simulate zoom
    // and let the scroll container handle the panning if the content is larger.
    if iv.image.Image != nil {
        originalSize := iv.image.Image.Bounds().Size()
        newWidth := float32(float64(originalSize.X) * iv.zoom)
        newHeight := float32(float64(originalSize.Y) * iv.zoom)
        
        iv.image.SetMinSize(fyne.NewSize(newWidth, newHeight))
        iv.image.Refresh()
    }
}
