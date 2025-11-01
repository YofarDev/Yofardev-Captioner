package dialogs

import (
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/dialog"
    "fyne.io/fyne/v2/widget"
    "log"
)

type SearchReplaceDialog struct {
    controller AppController
    dialog     dialog.Dialog
    searchEntry  *widget.Entry
    replaceEntry *widget.Entry
    onReplaceAll func(search, replace string)
}

func NewSearchReplaceDialog(controller AppController, parent fyne.Window) *SearchReplaceDialog {
    srd := &SearchReplaceDialog{
        controller: controller,
        searchEntry:  widget.NewEntry(),
        replaceEntry: widget.NewEntry(),
    }
    srd.searchEntry.SetPlaceHolder("Search for...")
    srd.replaceEntry.SetPlaceHolder("Replace with...")
    
    content := container.NewVBox(
        widget.NewLabel("Search and Replace"),
        widget.NewForm(
            widget.NewFormItem("Search:", srd.searchEntry),
            widget.NewFormItem("Replace:", srd.replaceEntry),
        ),
        widget.NewButton("Replace All", func() {
            if srd.onReplaceAll != nil {
                srd.onReplaceAll(srd.searchEntry.Text, srd.replaceEntry.Text)
            }
            srd.dialog.Hide()
        }),
    )
    
    srd.dialog = dialog.NewCustom("Search and Replace", "Close", content, parent)
    srd.dialog.Resize(fyne.NewSize(400, 250))
    
    return srd
}

func (srd *SearchReplaceDialog) Show(onReplaceAll func(search, replace string)) {
    srd.onReplaceAll = onReplaceAll
    log.Println("Showing search/replace dialog (placeholder)")
    srd.dialog.Show()
}
