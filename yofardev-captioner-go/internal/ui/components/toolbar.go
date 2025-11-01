package components

import (
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/theme"
    "fyne.io/fyne/v2/widget"
    "log"

    "github.com/yofardev/captioner/internal/app/controller" // Import the new controller package
)

type Toolbar struct {
    widget.BaseWidget
    controller controller.AppController // Use the AppController from the new controller package
    toolbar    *widget.Toolbar
}

func NewToolbar(controller controller.AppController) *Toolbar {
    t := &Toolbar{
        controller: controller,
    }
    
    t.toolbar = widget.NewToolbar(
        widget.NewToolbarAction(theme.FolderOpenIcon(), func() {
            t.controller.OpenFolder()
        }),
        widget.NewToolbarSeparator(),
        widget.NewToolbarAction(theme.DocumentSaveIcon(), func() {
            imagePath := t.controller.GetCurrentImagePath()
            caption := t.controller.GetCaptionEditorContent()
            if err := t.controller.SaveCaption(imagePath, caption); err != nil {
                t.controller.ShowError(err)
            } else {
                t.controller.ShowMessage("Caption saved successfully!")
            }
        }),
        widget.NewToolbarAction(theme.MediaPlayIcon(), func() {
            imagePath := t.controller.GetCurrentImagePath()
            prompt := t.controller.GetCaptionEditorContent() // Assuming caption editor content is the prompt
            if imagePath == "" {
                t.controller.ShowMessage("Please select an image first.")
                return
            }
            if prompt == "" {
                t.controller.ShowMessage("Please enter a prompt for caption generation.")
                return
            }
            
            generatedCaption, err := t.controller.GenerateCaptionForImage(t.controller.GetWindow(), imagePath, prompt)
            if err != nil {
                t.controller.ShowError(err)
            } else {
                // Update the caption editor with the generated caption
                // This requires the CaptionEditor to have a SetCaption method, which it does.
                // However, the toolbar doesn't have direct access to the CaptionEditor instance.
                // The AppController needs a method to update the caption editor.
                // For now, we'll just show the message.
                t.controller.ShowMessage("Caption generated: " + generatedCaption)
                // A more robust solution would be to have the AppController update the CaptionEditor directly.
                // For now, we'll rely on the AppController's RefreshUI or a specific method to update the editor.
            }
        }),
        widget.NewToolbarSeparator(),
        widget.NewToolbarAction(theme.SettingsIcon(), func() {
            log.Println("Settings clicked (placeholder)")
            // Implement settings dialog logic here
        }),
    )
    
    return t
}

func (t *Toolbar) Container() *fyne.Container {
    return container.NewMax(t.toolbar)
}
