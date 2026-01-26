# Folder Structure

This document describes the organization of the Mawney Partners API repository.

## Core Application Files

- `app.py` - Main Flask application with all API endpoints
- `config.py` - Configuration settings
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python runtime version
- `Procfile` - Process file for deployment (Render.com)
- `render.yaml` - Render deployment configuration

## AI & Processing Modules

- `custom_ai_assistant.py` - AI assistant system for CV formatting and queries
- `ai_memory_system.py` - AI memory and learning system
- `file_analyzer.py` - File analysis for attachments
- `data_collector.py` - RSS feed data collection
- `data_processor.py` - Article processing and categorization

## CV Formatting System

### Formatters (Active Versions)
- `enhanced_cv_formatter_v33.py` - Latest version (primary)
- `enhanced_cv_formatter_v31.py` - Fallback version
- `enhanced_cv_formatter_v20.py` - Fallback version
- `enhanced_cv_formatter_v17.py` - Fallback version
- `cv_formatter.py` - Base formatter
- `mawney_template_formatter.py` - Template formatter

### Templates (Active Versions)
- `mawney_cv_template_wkwebview_compatible_v33.html` - Latest template
- `mawney_cv_template_css_pages_v31.html` - Fallback template
- `mawney_cv_template_simple_a4_v20.html` - Fallback template
- `mawney_cv_template_force_pages_v17.html` - Fallback template
- `mawney_cv_template_correct.html` - Reference template

### CV Generation
- `cv_file_generator.py` - CV file generation system

## Data & Configuration

- `ai_memory.json` - AI memory storage
- `cv_style_analysis.json` - CV style analysis data
- `job_advert_style_analysis.json` - Job advert style analysis

## Directories

- `assets/` - Static assets (logos, images)
- `data/` - Data storage (gitignored, regenerated)
- `generated_cvs/` - Generated CV files (gitignored)
- `example-cvs/` - Example CV files for testing
- `example-job-adverts/` - Example job adverts for testing
- `docs/` - Documentation files
- `archive/` - Archived old versions (gitignored)

## Documentation

- `README.md` - Main project documentation
- `docs/AI_ASSISTANT_IMPROVEMENTS.md` - AI assistant improvements log
- `docs/API_ALIGNMENT_CHECK.md` - API endpoint alignment documentation
- `docs/FOLDER_STRUCTURE.md` - This file

## Notes

- Old versions of formatters and templates are kept as fallbacks
- The system tries formatters in order: v33 → v31 → v20 → v17
- Generated files and cache are gitignored but directories are preserved
- Example files are kept for testing and reference
