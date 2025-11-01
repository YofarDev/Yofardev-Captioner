package components

import (
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/widget"
    "log"

    "github.com/yofardev/captioner/internal/app/controller" // Import the new controller package
)

type CaptionEditor struct {
    widget.BaseWidget
    controller controller.AppController // Use the AppController from the new controller package
    entry      *widget.Entry
    onSave     func(string)
}

func NewCaptionEditor(controller controller.AppController) *CaptionEditor {
    ce := &CaptionEditor{
        controller: controller,
        entry:      widget.NewMultiLineEntry(),
    }
    ce.entry.SetPlaceHolder("Enter caption here...")
    ce.entry.Wrapping = fyne.TextWrapWord
    
    return ce
}

func (ce *CaptionEditor) Container() *fyne.Container {
    return container.NewMax(ce.entry)
}

func (ce *CaptionEditor) SetCaption(caption string) {
    ce.entry.SetText(caption)
}

func (ce *CaptionEditor) GetCaption() string {
    return ce.entry.Text
}

func (ce *CaptionEditor) SetPrompt(prompt string) {
    // This is a placeholder for now, as the prompt is separate from the caption
    // In the future, this might be used to set a default prompt in the editor
    log.Printf("Setting prompt in caption editor (placeholder): %s", prompt)
}

func (ce *CaptionEditor) GetPrompt() string {
    // This is a placeholder for now. The actual prompt might come from a separate dialog.
    return ce.entry.Text // For now, assume caption is also the prompt
}

func (ce *CaptionEditor) Save() {
	caption := ce.entry.Text
	imagePath := ce.controller.GetCurrentImagePath()
	if imagePath == "" {
		log.Println("No image selected, cannot save caption.")
		return
	}
	if err := ce.controller.SaveCaption(imagePath, caption); err != nil {
		log.Printf("Error saving caption: %v", err)
		ce.controller.ShowError(err)
		return
	}
	if ce.onSave != nil {
		ce.onSave(caption)
	}
	log.Println("Caption saved.")
}

func (ce *CaptionEditor) OnSave(callback func(string)) {
    ce.onSave = callback
}
