package dialogs

import (
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/dialog"
    "fyne.io/fyne/v2/widget"
    "log"
)

type PromptDialog struct {
    controller AppController
    dialog     dialog.Dialog
    entry      *widget.Entry
    onConfirm  func(string)
}

func NewPromptDialog(controller AppController, parent fyne.Window) *PromptDialog {
    pd := &PromptDialog{
        controller: controller,
        entry:      widget.NewMultiLineEntry(),
    }
    pd.entry.SetPlaceHolder("Enter prompt for caption generation...")
    pd.entry.Wrapping = fyne.TextWrapWord
    
    content := container.NewVBox(
        widget.NewLabel("Edit Prompt:"),
        pd.entry,
    )
    
    pd.dialog = dialog.NewCustomConfirm(
        "Edit Prompt",
        "Generate",
        "Cancel",
        content,
        func(b bool) {
            if b && pd.onConfirm != nil {
                pd.onConfirm(pd.entry.Text)
            }
        },
        parent,
    )
    pd.dialog.Resize(fyne.NewSize(500, 400))
    
    return pd
}

func (pd *PromptDialog) Show(currentPrompt string, onConfirm func(string)) {
    pd.entry.SetText(currentPrompt)
    pd.onConfirm = onConfirm
    log.Println("Showing prompt dialog (placeholder)")
    pd.dialog.Show()
}
