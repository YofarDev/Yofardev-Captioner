package components

import (
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/widget"
    "log"

    "github.com/yofardev/captioner/internal/app/controller" // Import the new controller package
)

type ImageList struct {
    widget.BaseWidget
    controller controller.AppController // Use the AppController from the new controller package
    list       *widget.List
    imagePaths []string
    onSelect   func(string)
}

func NewImageList(controller controller.AppController) *ImageList {
    il := &ImageList{
        controller: controller,
        imagePaths: []string{},
    }
    
    il.list = widget.NewList(
        func() int {
            return len(il.imagePaths)
        },
        func() fyne.CanvasObject {
            return widget.NewLabel("template")
        },
        func(id widget.ListItemID, obj fyne.CanvasObject) {
            obj.(*widget.Label).SetText(il.imagePaths[id])
        },
    )
    
    il.list.OnSelected = func(id widget.ListItemID) {
        if id >= 0 && id < len(il.imagePaths) {
            selectedPath := il.imagePaths[id]
            if il.onSelect != nil {
                il.onSelect(selectedPath)
            }
        }
    }
    
    return il
}

func (il *ImageList) Container() *fyne.Container {
    return container.NewMax(il.list)
}

func (il *ImageList) LoadFolder(folderPath string) {
    images, err := il.controller.ListImagesInFolder(folderPath)
    if err != nil {
        log.Printf("Error loading images from folder %s: %v", folderPath, err)
        return
    }
    il.imagePaths = images
    il.list.Refresh()
}

func (il *ImageList) OnSelect(callback func(string)) {
    il.onSelect = callback
}
