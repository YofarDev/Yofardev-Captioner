package ui

import (
    "context"
    "fmt"
    "image"
    "log"
    
    "fyne.io/fyne/v2"
    "fyne.io/fyne/v2/app"
    "fyne.io/fyne/v2/container"
    "fyne.io/fyne/v2/dialog"
    "fyne.io/fyne/v2/driver/desktop"
    
    "github.com/yofardev/captioner/internal/config"
    "github.com/yofardev/captioner/internal/models"
    "github.com/yofardev/captioner/internal/services"
    "github.com/yofardev/captioner/internal/storage"
    "github.com/yofardev/captioner/internal/ui/components"
)

type App struct {
    fyneApp    fyne.App
    window     fyne.Window
    config     *config.Config
    
    // Services
    captionSvc *services.CaptionService
    imageSvc   *services.ImageService
    sessionSvc *services.SessionService
    
    // UI Components
    imageList     *components.ImageList
    imageViewer   *components.ImageViewer
    captionEditor *components.CaptionEditor
    modelSelector *components.ModelSelector
    toolbar       *components.Toolbar
    
    // State
    currentFolder string
    currentImage  string
    fileMap       map[string]string
}

func NewApp(cfg *config.Config) *App {
    a := &App{
        config:  cfg,
        fileMap: make(map[string]string),
    }
    
    // Initialize Fyne app
    a.fyneApp = app.NewWithID("com.yofardev.captioner")
    a.window = a.fyneApp.NewWindow("Yofardev Captioner")
    
    // Initialize services
    a.initServices()
    
    // Initialize UI
    a.initComponents()
    a.setupLayout()
    a.bindEvents()
    
    // Load previous session
    a.loadSession()
    
    return a
}

func (a *App) initServices() {
    registry := models.NewRegistry()
    
    // Register all models
    for name, modelConfig := range a.config.Models {
        var model models.Model
        var err error
        switch modelConfig.Type {
        case "openai":
            model, err = models.NewOpenAIModel(name, modelConfig.BaseURL, modelConfig.ModelName, modelConfig.APIKeyEnv)
        case "mistral":
            model, err = models.NewMistralModel(name, modelConfig.ModelName, modelConfig.APIKeyEnv)
        case "florence2":
            // Temporarily comment out Florence2 until ONNX integration is stable
            // model = models.NewFlorence2Model()
            log.Printf("Florence2 model is temporarily disabled.")
            continue
        default:
            log.Printf("Unknown model type: %s for model %s", modelConfig.Type, name)
            continue
        }
        
        if err != nil {
            log.Printf("Failed to create model %s: %v", name, err)
            continue
        }
        
        if err := registry.Register(name, model); err != nil {
            log.Fatalf("Failed to register model %s: %v", name, err)
        }
    }
    
    a.captionSvc = services.NewCaptionService(registry)
    a.imageSvc = services.NewImageService()
    
    sessionSvc, err := services.NewSessionService(a.config)
    if err != nil {
        log.Fatalf("Failed to create session service: %v", err)
    }
    a.sessionSvc = sessionSvc
}

func (a *App) initComponents() {
    a.imageList = components.NewImageList(a) // Pass 'a' as controller.AppController
    a.imageViewer = components.NewImageViewer(a)
    a.captionEditor = components.NewCaptionEditor(a)
    a.modelSelector = components.NewModelSelector(a)
    a.toolbar = components.NewToolbar(a)
}

func (a *App) setupLayout() {
    // Left panel: image list
    leftPanel := container.NewBorder(
        nil, nil, nil, nil,
        a.imageList.Container(),
    )
    
    // Right panel: toolbar, image viewer, model selector, caption editor
    rightPanel := container.NewBorder(
        a.toolbar.Container(),
        container.NewVBox(
            a.modelSelector.Container(),
            a.captionEditor.Container(),
        ),
        nil, nil,
        a.imageViewer.Container(),
    )
    
    // Main split container
    split := container.NewHSplit(leftPanel, rightPanel)
    split.SetOffset(0.25)
    
    a.window.SetContent(split)
    a.window.Resize(fyne.NewSize(1200, 800))
    a.window.CenterOnScreen()
}

func (a *App) bindEvents() {
    // Keyboard shortcuts
    a.window.Canvas().AddShortcut(&desktop.CustomShortcut{
        KeyName:  fyne.KeyS,
        Modifier: desktop.ControlModifier,
    }, func(shortcut fyne.Shortcut) {
        a.captionEditor.Save()
    })
    
    // Image selection
    a.imageList.OnSelect(func(path string) {
        a.displayImage(path)
    })
    
    // Drag and drop for folders
    a.window.SetOnDropped(func(pos fyne.Position, uris []fyne.URI) {
        for _, uri := range uris {
            if uri.Scheme() == "file" {
                // Check if it's a directory by trying to list it
                _, ok := uri.(fyne.ListableURI)
                if ok {
                    a.currentFolder = uri.Path()
                    a.imageList.LoadFolder(uri.Path())
                    a.saveSession()
                    log.Printf("Dropped folder: %s", uri.Path())
                    return // Only handle the first dropped folder
                }
            }
        }
    })
    
    // Window close
    a.window.SetCloseIntercept(func() {
        a.saveSession()
        a.window.Close()
    })
}

func (a *App) Run() error {
    a.window.ShowAndRun()
    return nil
}

func (a *App) loadSession() {
    // Load previous session
    session, err := a.sessionSvc.Load(context.Background())
    if err != nil {
        log.Printf("Failed to load session: %v", err)
        return
    }
    
    a.currentFolder = session.CurrentFolder
    a.fileMap = session.FileMap
    a.modelSelector.SetModel(session.SelectedModel)
    
    if a.currentFolder != "" {
        a.imageList.LoadFolder(a.currentFolder)
    }
}

func (a *App) saveSession() {
    session := &storage.Session{
        CurrentFolder: a.currentFolder,
        CurrentImage:  a.currentImage,
        FileMap:       a.fileMap,
        SelectedModel: a.modelSelector.GetModel(),
        PromptText:    a.captionEditor.GetPrompt(),
    }
    
    if err := a.sessionSvc.Save(context.Background(), session); err != nil {
        log.Printf("Failed to save session: %v", err)
    }
}

func (a *App) displayImage(path string) {
    a.currentImage = path
    a.imageViewer.SetImage(path)
    
    // Load caption for the image
    caption, err := a.sessionSvc.LoadCaption(context.Background(), path)
    if err != nil {
        log.Printf("Failed to load caption for image %s: %v", path, err)
        a.captionEditor.SetCaption("") // Clear caption if not found
    } else {
        a.captionEditor.SetCaption(caption)
    }
}

// AppController methods implementation
func (a *App) ListImagesInFolder(folderPath string) ([]string, error) {
    return a.imageSvc.ListImagesInFolder(folderPath)
}

func (a *App) GetImage(imagePath string) (image.Image, error) {
    return a.imageSvc.LoadImage(imagePath)
}

func (a *App) GetImageThumbnail(imagePath string, size fyne.Size) (fyne.Resource, error) {
    return a.imageSvc.LoadImageThumbnail(imagePath, size)
}

func (a *App) SaveCaption(imagePath, caption string) error {
    if imagePath == "" {
        return fmt.Errorf("no image selected to save caption for")
    }
    if err := a.sessionSvc.SaveCaption(context.Background(), imagePath, caption); err != nil {
        return fmt.Errorf("failed to save caption for image %s: %w", imagePath, err)
    }
    log.Printf("Caption saved for image %s", imagePath)
    return nil
}

func (a *App) LoadCaption(imagePath string) (string, error) {
    if imagePath == "" {
        return "", fmt.Errorf("no image selected to load caption for")
    }
    caption, err := a.sessionSvc.LoadCaption(context.Background(), imagePath)
    if err != nil {
        return "", fmt.Errorf("failed to load caption for image %s: %w", imagePath, err)
    }
    return caption, nil
}

func (a *App) ListModels() []string {
    return a.captionSvc.ListModels()
}

func (a *App) GetSelectedModel() string {
    return a.modelSelector.GetModel()
}

func (a *App) SetSelectedModel(modelName string) {
    a.modelSelector.SetModel(modelName)
}

func (a *App) GenerateCaptionForImage(ctx fyne.Window, imagePath, prompt string) (string, error) {
    if imagePath == "" {
        return "", fmt.Errorf("no image selected to generate caption for")
    }
    selectedModel := a.modelSelector.GetModel()
    if selectedModel == "" {
        return "", fmt.Errorf("no model selected for caption generation")
    }
    log.Printf("Generating caption for image %s using model %s...", imagePath, selectedModel)
    caption, err := a.captionSvc.GenerateCaption(context.Background(), selectedModel, imagePath, prompt)
    if err != nil {
        return "", fmt.Errorf("failed to generate caption for image %s: %w", imagePath, err)
    }
    log.Printf("Caption generated for image %s", imagePath)
    return caption, nil
}

func (a *App) LoadSession(sessionPath string) error {
    // This method is handled internally by App.loadSession()
    // For external calls, we might need a more specific implementation or
    // decide if this method should be exposed via the controller.
    // For now, we'll just call the internal loadSession.
    a.loadSession()
    return nil
}

func (a *App) SaveSession(sessionPath string) error {
    // This method is handled internally by App.saveSession()
    // For external calls, we might need a more specific implementation or
    // decide if this method should be exposed via the controller.
    // For now, we'll just call the internal saveSession.
    a.saveSession()
    return nil
}

func (a *App) GetLastOpenedFolder() string {
    return a.sessionSvc.GetLastOpenedFolder()
}

func (a *App) SetLastOpenedFolder(folderPath string) {
    a.sessionSvc.SetLastOpenedFolder(folderPath)
}

func (a *App) ShowError(err error) {
    dialog.ShowError(err, a.window)
}

func (a *App) ShowMessage(message string) {
    dialog.ShowInformation("Information", message, a.window)
}

func (a *App) RefreshUI() {
    a.imageList.Refresh()
    a.imageViewer.Refresh()
    a.captionEditor.Refresh()
    a.modelSelector.Refresh()
    a.toolbar.Refresh()
}

func (a *App) GetCurrentImagePath() string {
    return a.currentImage
}

func (a *App) GetCaptionEditorContent() string {
    return a.captionEditor.GetCaption()
}

func (a *App) GetWindow() fyne.Window {
    return a.window
}

func (a *App) OpenFolder() {
	dialog.ShowFolderOpen(func(uri fyne.ListableURI, err error) {
		if err != nil {
			log.Printf("Error opening folder dialog: %v", err)
			a.ShowError(err)
			return
		}
		if uri == nil {
			return // User cancelled
		}
		
		folderPath := uri.Path()
		a.currentFolder = folderPath
		a.imageList.LoadFolder(folderPath)
		a.saveSession()
		log.Printf("Opened folder: %s", folderPath)
	}, a.window)
}
