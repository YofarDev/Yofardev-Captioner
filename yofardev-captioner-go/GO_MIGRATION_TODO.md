# Go Migration Feature Comparison & TODO List

## Executive Summary

This document compares the original Python Yofardev Captioner application with the Go migration, identifying missing features and implementation gaps that need to be addressed.

---

## Feature Comparison Matrix

### ✅ Core Features (Implemented in Go)

| Feature | Python | Go | Status |
|---------|--------|----|----|
| Basic UI Framework | Tkinter | Fyne | ✅ Complete |
| Image Loading | PIL | Go image libs | ✅ Complete |
| Caption Storage | Text files | Text files + SQLite | ✅ Complete |
| Session Persistence | JSON file | SQLite | ✅ Complete |
| Model Registry | Hardcoded | Dynamic registry | ✅ Complete |
| OpenAI API Support | ✅ | ✅ | ✅ Complete |
| Mistral API Support | ✅ | ✅ | ✅ Complete |
| Configuration Management | settings.py | Viper + YAML | ✅ Complete |
| Logging | print() | Logrus | ✅ Complete |

### ⚠️ Partially Implemented Features

| Feature | Python Implementation | Go Implementation | Gap |
|---------|---------------------|-------------------|-----|
| **Thumbnail Display** | Custom ThumbnailListbox with PIL | Basic Fyne list | Missing: Square crop, color coding for caption status |
| **Search & Replace** | Full dialog with preview | Basic placeholder dialog | Missing: Preview, case sensitivity, file iteration |
| **Prompt Dialog** | Full editor with default button | Basic dialog | Missing: Default prompt button, better formatting |
| **Settings Dialog** | API key editor with .env | Not implemented | Missing: Complete settings UI |
| **Image Viewer** | Click to open in system app | Basic display | Missing: Click handler, resolution/size display |
| **Caption Editor** | Undo/Redo support | Basic text entry | Missing: Undo/Redo functionality |

### ❌ Missing Features in Go

| Feature | Python Implementation | Priority | Complexity |
|---------|---------------------|----------|------------|
| **Florence2 Local Model** | Full PyTorch implementation | HIGH | HIGH |
| **Batch Caption Generation** | "For all empty captions" mode | HIGH | MEDIUM |
| **Image Renaming Tool** | Rename files to sequential numbers | MEDIUM | LOW |
| **Caption Status Indicators** | Color-coded thumbnails (gray15/gray25) | HIGH | LOW |
| **Double-click Image Open** | Opens in system default app | LOW | LOW |
| **Trigger Phrase Rewriting** | `rewrite_caption_with_trigger_phrase()` | LOW | MEDIUM |
| **Image Size Validation** | Auto-resize if >5MB | MEDIUM | LOW |
| **Debounce for API Calls** | 6-second delay between calls | MEDIUM | LOW |
| **Natural Sorting** | Alphanumeric sort for filenames | LOW | LOW |
| **Refresh Images Button** | Reload folder contents | MEDIUM | LOW |
| **Open Current Folder** | Open folder in file explorer | LOW | LOW |
| **Window Centering** | Center on screen at startup | LOW | LOW |
| **Fixed Window Size** | Non-resizable window | LOW | LOW |
| **Keyboard Shortcuts** | Ctrl+Z, Ctrl+Y for undo/redo | MEDIUM | LOW |
| **Caption Mode Radio Buttons** | Single vs All empty | HIGH | LOW |

---

## Detailed Feature Analysis

### 1. Thumbnail System (HIGH PRIORITY)

**Python Implementation:**
- Custom `ThumbnailListbox` class with `ThumbnailItem` widgets
- Square aspect ratio with BoxFit.cover effect (crop to fit)
- Color coding: `gray15` (no caption), `gray25` (has caption), `lavender blush` (selected)
- Double-click to open image in system app
- Mousewheel scrolling support

**Go Current State:**
- Basic Fyne list widget
- No thumbnail preview
- No color coding for caption status
- No double-click handler

**Required Implementation:**
```go
// Need to implement:
- Square thumbnail generation with center crop
- Caption status checking (file exists and not empty)
- Color-coded backgrounds based on caption status
- Double-click handler for opening images
- Proper thumbnail caching
```

### 2. Search & Replace Dialog (HIGH PRIORITY)

**Python Implementation:**
- Search with case-sensitive option
- Preview changes before applying
- Shows line numbers and match counts
- Iterates through all caption files
- Updates current caption if modified
- Regex support for case-insensitive matching

**Go Current State:**
- Basic placeholder dialog
- No preview functionality
- No file iteration logic
- No case sensitivity option

**Required Implementation:**
```go
// Need to implement:
- GetCaptionFiles() - list all .txt files for loaded images
- SearchInFiles() - find matches with line numbers
- PreviewReplacements() - show what will change
- ApplyReplacements() - perform actual replacements
- Case-sensitive toggle
- Refresh current caption after changes
```

### 3. Batch Caption Generation (HIGH PRIORITY)

**Python Implementation:**
- Radio buttons: "For this image" vs "For all empty captions"
- Iterates through all images
- Checks if caption file is empty before generating
- Applies debounce for API calls (6 seconds)
- Updates UI for currently selected image

**Go Current State:**
- Only single image caption generation
- No batch mode
- No empty caption checking
- No debounce mechanism

**Required Implementation:**
```go
// Need to implement:
- Caption mode selection (single/batch)
- Empty caption detection
- Batch processing with progress indicator
- API call debouncing (6 seconds between calls)
- Skip Florence2 from debounce (local model)
```

### 4. Florence2 Model Integration (HIGH PRIORITY)

**Python Implementation:**
- Full PyTorch model loading
- HuggingFace model download
- Three detail modes: CAPTION, DETAILED_CAPTION, MORE_DETAILED_CAPTION
- Flash attention workaround
- Trigger phrase integration

**Go Current State:**
- Temporarily disabled due to ONNX Runtime issues
- Basic structure exists but not functional

**Required Implementation:**
```go
// Options:
1. Wait for stable ONNX Runtime Go bindings
2. Use Python subprocess to call Florence2
3. Use HTTP API to Python service
4. Use alternative Go-native vision model
```

### 5. Image Utilities (MEDIUM PRIORITY)

**Python Implementation:**
- Auto-resize images >5MB before API upload
- Iterative quality reduction (90 -> 10)
- Dimension scaling if quality reduction insufficient
- Temporary file cleanup
- Base64 encoding with MIME type detection

**Go Current State:**
- Basic image loading and resizing
- No size validation
- No automatic compression

**Required Implementation:**
```go
// Need to implement:
- CheckImageSize() - validate file size
- ResizeIfNeeded() - compress to <5MB
- Iterative quality reduction
- Temporary file management
```

### 6. Caption Editor Enhancements (MEDIUM PRIORITY)

**Python Implementation:**
- Undo/Redo with Ctrl+Z/Ctrl+Y
- Auto-save on image change
- Configurable font (Verdana, 18pt)
- Word wrapping
- Padding and borders

**Go Current State:**
- Basic multiline entry
- Manual save only
- No undo/redo

**Required Implementation:**
```go
// Need to implement:
- Undo/Redo stack
- Keyboard shortcuts (Ctrl+Z, Ctrl+Y)
- Auto-save on image selection change
- Better text formatting options
```

### 7. Image Renaming Tool (MEDIUM PRIORITY)

**Python Implementation:**
- Renames all images to sequential numbers (001, 002, etc.)
- Maintains sort order
- Renames associated .txt files
- Two-pass rename to avoid conflicts
- Padding based on total file count

**Go Current State:**
- Not implemented

**Required Implementation:**
```go
// Need to implement:
- RenameFilesToNumbers() function
- Natural sort before renaming
- Two-pass rename (temp names first)
- Caption file renaming
- Padding calculation
```

### 8. Settings Dialog (MEDIUM PRIORITY)

**Python Implementation:**
- Edit API keys: GITHUB_API_KEY, MISTRAL_API_KEY, GEMINI_API_KEY
- Save to .env file
- Load existing values
- Simple form layout

**Go Current State:**
- Not implemented

**Required Implementation:**
```go
// Need to implement:
- Settings dialog with API key fields
- .env file reading/writing
- Secure key storage
- Validation
```

### 9. Additional Models (LOW PRIORITY)

**Python Models:**
- Gemini 2.5 Flash
- Gemini 2.5 Pro
- Qwen2.5 72B
- GPT-4.1
- Grok
- Pixtral
- Florence2

**Go Models:**
- OpenAI-compatible (generic)
- Mistral
- Florence2 (disabled)

**Required Implementation:**
```go
// Need to add to config:
- Gemini API configuration
- Qwen configuration
- Grok configuration
- Model-specific parameters
```

---

## Implementation Priority

### Phase 1: Critical Features (Week 1-2)
1. ✅ Batch caption generation with empty caption detection
2. ✅ Caption status indicators (color-coded thumbnails)
3. ✅ Search & Replace with preview
4. ✅ Debounce mechanism for API calls
5. ✅ Image size validation and compression

### Phase 2: Important Features (Week 3-4)
6. ✅ Settings dialog for API keys
7. ✅ Undo/Redo in caption editor
8. ✅ Image renaming tool
9. ✅ Refresh images functionality
10. ✅ Natural sorting for filenames

### Phase 3: Nice-to-Have Features (Week 5-6)
11. ✅ Double-click to open images
12. ✅ Open current folder in explorer
13. ✅ Trigger phrase rewriting
14. ✅ Window positioning and sizing
15. ✅ Additional model configurations

### Phase 4: Advanced Features (Future)
16. ⏳ Florence2 local model integration
17. ⏳ Progress indicators for batch operations
18. ⏳ Advanced thumbnail caching
19. ⏳ Keyboard shortcut customization
20. ⏳ Multi-language support

---

## Technical Debt & Improvements

### Code Quality
- [ ] Add comprehensive unit tests for all services
- [ ] Add integration tests for UI components
- [ ] Improve error handling with custom error types
- [ ] Add context cancellation for long operations
- [ ] Implement proper logging levels

### Performance
- [ ] Optimize thumbnail generation and caching
- [ ] Implement lazy loading for large image folders
- [ ] Add connection pooling for API clients
- [ ] Profile memory usage and fix leaks
- [ ] Optimize SQLite queries

### User Experience
- [ ] Add loading spinners for async operations
- [ ] Implement progress bars for batch processing
- [ ] Add keyboard navigation for image list
- [ ] Improve error messages and user feedback
- [ ] Add tooltips and help text

### Architecture
- [ ] Complete AppController interface implementation
- [ ] Add dependency injection for better testability
- [ ] Implement event bus for component communication
- [ ] Add plugin system for custom models
- [ ] Improve configuration validation

---

## Migration Blockers

### Critical Issues
1. **Florence2 Integration**: ONNX Runtime Go bindings have generic type issues
   - **Solution Options**: 
     - Wait for library updates
     - Use Python subprocess
     - Use HTTP API wrapper
     - Switch to alternative model

2. **Thumbnail Performance**: Need efficient caching for large folders
   - **Solution**: Implement LRU cache with disk persistence

3. **API Rate Limiting**: Need proper debounce and retry logic
   - **Solution**: Implement rate limiter with exponential backoff

### Non-Critical Issues
1. **UI Polish**: Fyne widgets need styling to match Python version
2. **Testing**: Need comprehensive test coverage
3. **Documentation**: Need user guide and API documentation

---

## Success Criteria

### Functional Parity
- [ ] All Python features working in Go
- [ ] Same or better performance
- [ ] Same or better user experience
- [ ] No data loss during migration

### Quality Metrics
- [ ] >80% test coverage
- [ ] <100ms UI response time
- [ ] <500MB memory usage
- [ ] Zero critical bugs

### User Acceptance
- [ ] Positive feedback from beta testers
- [ ] Successful migration of existing users
- [ ] Documentation completeness
- [ ] Platform compatibility (macOS, Linux, Windows)

---

## Next Steps

1. **Review this document** with stakeholders
2. **Prioritize features** based on user needs
3. **Create detailed implementation plans** for Phase 1 features
4. **Set up testing infrastructure** before implementing new features
5. **Begin Phase 1 implementation** with batch caption generation

---

## Notes

- The Go version has better architecture (services, interfaces, dependency injection)
- SQLite storage is more robust than JSON files
- Configuration management is more flexible with Viper
- Need to maintain backward compatibility with Python caption files
- Consider gradual rollout with feature flags

---

**Document Version**: 1.0  
**Last Updated**: 2025-11-01  
**Author**: Migration Team  
**Status**: Ready for Review