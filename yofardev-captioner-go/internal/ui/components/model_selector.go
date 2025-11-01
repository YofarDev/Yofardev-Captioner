package components

import (
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/widget"
    "log"

    "github.com/yofardev/captioner/internal/app/controller" // Import the new controller package
)

type ModelSelector struct {
    widget.BaseWidget
    controller controller.AppController // Use the AppController from the new controller package
    selector   *widget.Select
    models     []string
    selected   string
    onSelect   func(string)
}

func NewModelSelector(controller controller.AppController) *ModelSelector {
    ms := &ModelSelector{
        controller: controller,
        models:     []string{"Loading models..."}, // Initial placeholder
    }
    
    ms.selector = widget.NewSelect(ms.models, func(s string) {
        ms.selected = s
        if ms.onSelect != nil {
            ms.onSelect(s)
        }
        log.Printf("Selected model: %s", s)
    })
    
    // In a real app, you'd load models from the controller
    // For now, we'll simulate it.
    ms.loadModels()
    
    return ms
}

func (ms *ModelSelector) Container() *fyne.Container {
    return container.NewMax(ms.selector)
}

func (ms *ModelSelector) loadModels() {
    ms.models = ms.controller.ListModels()
    ms.selector.Options = ms.models
    if len(ms.models) > 0 {
        ms.selected = ms.models[0]
        ms.selector.SetSelected(ms.selected)
    }
    ms.selector.Refresh()
}

func (ms *ModelSelector) SetModel(modelName string) {
    ms.selected = modelName
    ms.selector.SetSelected(modelName)
}

func (ms *ModelSelector) GetModel() string {
    return ms.selected
}

func (ms *ModelSelector) OnSelect(callback func(string)) {
    ms.onSelect = callback
}
