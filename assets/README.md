# Mawney Partners Logo Assets

## ✅ Logo Files Added

Your two logo files have been placed in this directory:

### 1. Top Logo (Header)
- **Filename:** `cv logo 1.png` ✅
- **Usage:** CV header (top of document)
- **Position:** Top-center, above candidate name
- **Size:** Max 250px wide
- **Format:** PNG

### 2. Bottom Logo (Footer)
- **Filename:** `cv logo 2.png` ✅
- **Usage:** CV footer (bottom of document)
- **Position:** Bottom-center, after all sections
- **Size:** Max 200px wide
- **Format:** PNG with subtle opacity (0.8)

## File Structure

```
/Users/hopegilbert/Desktop/mawney-api-clean/assets/
├── README.md (this file)
├── cv logo 1.png ✅ (TOP LOGO - in header)
└── cv logo 2.png ✅ (BOTTOM LOGO - in footer)
```

## Current Configuration

The CV formatter is configured to use:
- **Font:** Garamond (EB Garamond web font)
- **Top Logo:** `assets/cv logo 1.png` (header)
- **Bottom Logo:** `assets/cv logo 2.png` (footer)
- **Position:** Center-aligned for both

## CV Layout

```
┌─────────────────────────────────┐
│      [TOP LOGO - cv logo 1]     │
│                                 │
│      CANDIDATE NAME             │
│      Contact Information        │
├─────────────────────────────────┤
│                                 │
│      CV CONTENT                 │
│      (All sections)             │
│                                 │
├─────────────────────────────────┤
│    [BOTTOM LOGO - cv logo 2]    │
└─────────────────────────────────┘
```

## Customization

If you want to change logo settings, update in `cv_formatter.py`:

```python
"branding": {
    "top_logo_path": "assets/cv logo 1.png",
    "bottom_logo_path": "assets/cv logo 2.png",
    "use_top_logo": True,
    "use_bottom_logo": True,
    "logo_position": "center"
}
```

