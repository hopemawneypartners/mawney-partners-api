# Mawney Partners Logo Assets

## Logo Files Required

Place your two logo files in this directory:

### 1. Main Logo
- **Filename:** `mawney_logo.png`
- **Usage:** CV headers, documents, professional materials
- **Recommended size:** 200-400px wide
- **Format:** PNG with transparent background preferred

### 2. Alternative Logo
- **Filename:** `mawney_logo_alt.png` (or `mawney_logo_white.png` if it's a white version)
- **Usage:** Alternative styling, dark backgrounds
- **Recommended size:** 200-400px wide
- **Format:** PNG with transparent background preferred

## File Structure

```
/Users/hopegilbert/Desktop/mawney-api-clean/assets/
├── README.md (this file)
├── mawney_logo.png (place your first logo here)
└── mawney_logo_alt.png (place your second logo here)
```

## Current Usage

The CV formatter is configured to use:
- **Font:** Garamond (EB Garamond web font)
- **Logo:** `assets/mawney_logo.png`
- **Position:** Top-center of CV

## To Add Your Logos

Simply copy your two logo PNG files into this directory and rename them as specified above.

If your logos have different names or you want to use different positioning, update the configuration in `cv_formatter.py`:

```python
"branding": {
    "logo_path": "assets/mawney_logo.png",
    "use_logo": True,
    "logo_position": "top-center"  # or "top-left", "top-right"
}
```

