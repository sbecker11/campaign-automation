# Product Image Configuration Options

## Overview

When configuring products in your campaign YAML, you can choose to either generate new images with AI or use existing product photos. You can also mix both approaches in a single campaign.

## Option 1: Generate with AI (Default)

Use AI (DALL-E 3) to generate product images from descriptions.

```yaml
products:
  - product_id: "new_product"
    name: "Product Name"
    description: "Detailed description for AI generation"
    generate_new: true
```

**Requirements:**
- `generate_new: true` (or omit, as `true` is the default)
- `description`: Required - detailed description used by AI to generate the image

**Process:**
- AI generates a base image from the description
- Image is saved to `products/product_id/product_id_generated.png`
- Image is then processed into all specified aspect ratios
- Logo and text are added to each variant
- All variants go through validation

**Time:** ~20 seconds per product (DALL-E API call)
**Cost:** ~$0.04 per product image

## Option 2: Use Existing Assets

Use your own product photos instead of generating new ones.

```yaml
products:
  - product_id: "existing_product"
    name: "Product Name"
    description: "Product description"
    generate_new: false
    existing_assets: "path/to/image/directory/"
```

**Requirements:**
- `generate_new: false` (required)
- `existing_assets`: Required - path to directory containing image files
- Directory must contain at least one PNG or JPG file
- The pipeline uses the **first** image file found in the directory

**Process:**
- Pipeline searches the `existing_assets` directory for PNG or JPG files
- Uses the first image found as the base image
- Image is then processed into all specified aspect ratios (same as AI-generated)
- Logo and text are added to each variant
- All variants go through validation

**Time:** ~5 seconds per product (no API call)
**Cost:** $0.00 (no API calls)

**Error Handling:**
- If `existing_assets` is not specified, pipeline returns an error
- If directory has no PNG or JPG files, pipeline returns an error

## Option 3: Mix Both Approaches

You can use both AI-generated and existing assets in the same campaign.

```yaml
products:
  - product_id: "new_product"
    name: "New Product"
    description: "Detailed description for AI generation"
    generate_new: true
  
  - product_id: "existing_product"
    name: "Existing Product"
    description: "Product description"
    generate_new: false
    existing_assets: "assets/existing/"
```

**Benefits:**
- Generate new images for products that don't have photos yet
- Use existing high-quality photos for products that already have them
- Optimize cost and time by choosing the best option per product

## Field Reference

### Product Fields

- **`product_id`** (required): Unique identifier for the product
- **`name`** (required): Display name for the product
- **`description`** (required if `generate_new: true`): Used by AI to generate product images
- **`generate_new`** (optional, default: `true`): 
  - `true`: Generate new image with AI
  - `false`: Use existing assets from `existing_assets` directory
- **`existing_assets`** (required if `generate_new: false`): Path to directory containing image files (PNG or JPG)

## Comparison

| Feature | AI Generation (`generate_new: true`) | Existing Assets (`generate_new: false`) |
|---------|-------------------------------------|------------------------------------------|
| **Time** | ~20 seconds per product | ~5 seconds per product |
| **Cost** | ~$0.04 per product | $0.00 |
| **Quality** | AI-generated, may vary | Your own photos, consistent quality |
| **Requirements** | Description required | Existing image file required |
| **Best For** | New products, concept products | Products with existing photos |

