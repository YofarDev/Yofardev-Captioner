package controller

import (
	"fyne.io/fyne/v2"
	"image"
)

// AppController defines the interface for application-wide control and data access.
// This interface is used by UI components to interact with the application's backend services
// without creating direct dependencies on the main application struct, thus preventing import cycles.
type AppController interface {
	// Image management
	ListImagesInFolder(folderPath string) ([]string, error)
	GetImage(imagePath string) (image.Image, error)
	GetImageThumbnail(imagePath string, size fyne.Size) (fyne.Resource, error)
	SaveCaption(imagePath, caption string) error
	LoadCaption(imagePath string) (string, error)

	// Model management
	ListModels() []string
	GetSelectedModel() string
	SetSelectedModel(modelName string)

	// Caption generation
	GenerateCaptionForImage(ctx fyne.Window, imagePath, prompt string) (string, error)

	// Session management
	LoadSession(sessionPath string) error
	SaveSession(sessionPath string) error
	GetLastOpenedFolder() string
	SetLastOpenedFolder(folderPath string)

	// UI interaction
	ShowError(err error)
	ShowMessage(message string)
	RefreshUI()
	OpenFolder() // Open folder dialog

	// State access for UI components
	GetCurrentImagePath() string
	GetCaptionEditorContent() string
	GetWindow() fyne.Window // Added to allow toolbar to pass window context for dialogs
}
