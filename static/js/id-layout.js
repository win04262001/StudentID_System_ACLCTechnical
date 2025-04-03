/**
 * ID Card Layout Enhancement
 * Handles barcode and signature processing for student ID cards
 */

// Barcode processing and fitting
class BarcodeProcessor {
  constructor(options = {}) {
    this.options = {
      padding: options.padding || 10,
      background: options.background || "#ffffff",
      lineColor: options.lineColor || "#000000",
      width: options.width || 2,
      height: options.height || 100,
      displayValue: options.displayValue || false,
      ...options,
    }
  }

  // Process and fit barcode to container
  processBarcode(barcodeElement, containerElement) {
    if (!barcodeElement || !containerElement) return

    // Get container dimensions
    const container = containerElement.getBoundingClientRect()
    const containerWidth = container.width - this.options.padding * 2
    const containerHeight = container.height - this.options.padding * 2

    // Calculate optimal dimensions
    const optimalWidth = Math.min(containerWidth, 300)
    const optimalHeight = Math.min(containerHeight, 80)

    // Apply JsBarcode with calculated dimensions
    if (barcodeElement.tagName === "SVG") {
      JsBarcode(barcodeElement, barcodeElement.dataset.value || "0000000000", {
        format: "CODE128",
        width: this.options.width,
        height: optimalHeight - 20,
        displayValue: this.options.displayValue,
        background: this.options.background,
        lineColor: this.options.lineColor,
        margin: 5,
      })

      // Adjust SVG dimensions
      barcodeElement.setAttribute("width", optimalWidth)
      barcodeElement.setAttribute("height", optimalHeight)
      barcodeElement.style.maxWidth = "100%"
      barcodeElement.style.maxHeight = "100%"
    } else if (barcodeElement.tagName === "IMG") {
      // For image barcodes, adjust size and position
      barcodeElement.style.maxWidth = optimalWidth + "px"
      barcodeElement.style.maxHeight = optimalHeight + "px"
      barcodeElement.style.objectFit = "contain"
      barcodeElement.style.display = "block"
      barcodeElement.style.margin = "0 auto"
    }

    // Center in container
    containerElement.style.display = "flex"
    containerElement.style.justifyContent = "center"
    containerElement.style.alignItems = "center"
    containerElement.style.padding = this.options.padding + "px"
  }

  // Generate a new barcode
  generateBarcode(value, format = "CODE128") {
    const canvas = document.createElement("canvas")
    JsBarcode(canvas, value, {
      format: format,
      width: this.options.width,
      height: this.options.height,
      displayValue: this.options.displayValue,
      background: this.options.background,
      lineColor: this.options.lineColor,
      margin: 5,
    })

    return canvas.toDataURL("image/png")
  }
}

// Signature processing and enhancement
class SignatureProcessor {
  constructor(options = {}) {
    this.options = {
      removeBackground: options.removeBackground !== false,
      enhanceContrast: options.enhanceContrast !== false,
      autoClean: options.autoClean !== false,
      maxWidth: options.maxWidth || 200,
      maxHeight: options.maxHeight || 80,
      padding: options.padding || 5,
      ...options,
    }
  }

  // Process signature image
  async processSignature(signatureElement, containerElement) {
    if (!signatureElement || !containerElement) return

    // Get container dimensions
    const container = containerElement.getBoundingClientRect()
    const containerWidth = container.width - this.options.padding * 2
    const containerHeight = container.height - this.options.padding * 2

    // Calculate optimal dimensions while maintaining aspect ratio
    const img = new Image()
    img.crossOrigin = "anonymous"

    return new Promise((resolve, reject) => {
      img.onload = () => {
        // Create canvas for processing
        const canvas = document.createElement("canvas")
        const ctx = canvas.getContext("2d")

        // Set canvas size
        const aspectRatio = img.width / img.height
        let width = Math.min(containerWidth, this.options.maxWidth)
        let height = width / aspectRatio

        // Adjust if height exceeds container
        if (height > containerHeight) {
          height = Math.min(containerHeight, this.options.maxHeight)
          width = height * aspectRatio
        }

        canvas.width = width
        canvas.height = height

        // Draw original image
        ctx.drawImage(img, 0, 0, width, height)

        // Process the signature
        if (this.options.removeBackground) {
          this.removeBackground(canvas)
        }

        if (this.options.enhanceContrast) {
          this.enhanceContrast(canvas)
        }

        if (this.options.autoClean) {
          this.cleanSignature(canvas)
        }

        // Update the signature element
        signatureElement.src = canvas.toDataURL("image/png")
        signatureElement.style.maxWidth = "100%"
        signatureElement.style.maxHeight = "100%"
        signatureElement.style.display = "block"
        signatureElement.style.margin = "0 auto"

        // Center in container
        containerElement.style.display = "flex"
        containerElement.style.justifyContent = "center"
        containerElement.style.alignItems = "center"
        containerElement.style.padding = this.options.padding + "px"

        resolve(canvas.toDataURL("image/png"))
      }

      img.onerror = () => {
        reject(new Error("Failed to load signature image"))
      }

      img.src = signatureElement.src
    })
  }

  // Remove background from signature
  removeBackground(canvas) {
    const ctx = canvas.getContext("2d")
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const data = imageData.data

    // Detect background color (assume corners represent background)
    const topLeft = this.getPixelColor(data, 0, 0, canvas.width)
    const topRight = this.getPixelColor(data, canvas.width - 1, 0, canvas.width)
    const bottomLeft = this.getPixelColor(data, 0, canvas.height - 1, canvas.width)
    const bottomRight = this.getPixelColor(data, canvas.width - 1, canvas.height - 1, canvas.width)

    // Calculate average background color
    const bgColor = {
      r: Math.round((topLeft.r + topRight.r + bottomLeft.r + bottomRight.r) / 4),
      g: Math.round((topLeft.g + topRight.g + bottomLeft.g + bottomRight.g) / 4),
      b: Math.round((topLeft.b + topRight.b + bottomLeft.b + bottomRight.b) / 4),
    }

    // Threshold for background detection (color similarity)
    const threshold = 30

    // Remove background
    for (let i = 0; i < data.length; i += 4) {
      const r = data[i]
      const g = data[i + 1]
      const b = data[i + 2]

      // Calculate color distance from background
      const distance = Math.sqrt(Math.pow(r - bgColor.r, 2) + Math.pow(g - bgColor.g, 2) + Math.pow(b - bgColor.b, 2))

      // If color is close to background, make it transparent
      if (distance < threshold) {
        data[i + 3] = 0 // Set alpha to 0 (transparent)
      }
    }

    ctx.putImageData(imageData, 0, 0)
  }

  // Enhance contrast of signature
  enhanceContrast(canvas) {
    const ctx = canvas.getContext("2d")
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const data = imageData.data

    // Find min and max values
    let min = 255
    let max = 0

    for (let i = 0; i < data.length; i += 4) {
      // Skip transparent pixels
      if (data[i + 3] === 0) continue

      const value = (data[i] + data[i + 1] + data[i + 2]) / 3
      min = Math.min(min, value)
      max = Math.max(max, value)
    }

    // Apply contrast stretching
    const range = max - min
    if (range > 0) {
      for (let i = 0; i < data.length; i += 4) {
        // Skip transparent pixels
        if (data[i + 3] === 0) continue

        // Enhance each channel
        for (let j = 0; j < 3; j++) {
          const value = data[i + j]
          data[i + j] = Math.round(((value - min) / range) * 255)
        }
      }
    }

    ctx.putImageData(imageData, 0, 0)
  }

  // Clean signature by removing noise
  cleanSignature(canvas) {
    const ctx = canvas.getContext("2d")
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height)
    const data = imageData.data
    const width = canvas.width
    const height = canvas.height

    // Create a copy of the image data
    const tempData = new Uint8ClampedArray(data)

    // Remove isolated pixels (noise)
    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        const idx = (y * width + x) * 4

        // Skip transparent pixels
        if (data[idx + 3] === 0) continue

        // Count non-transparent neighbors
        let neighbors = 0
        for (let dy = -1; dy <= 1; dy++) {
          for (let dx = -1; dx <= 1; dx++) {
            if (dx === 0 && dy === 0) continue

            const nx = x + dx
            const ny = y + dy
            const nidx = (ny * width + nx) * 4

            if (data[nidx + 3] > 0) {
              neighbors++
            }
          }
        }

        // If pixel has fewer than 2 neighbors, consider it noise
        if (neighbors < 2) {
          tempData[idx + 3] = 0 // Make transparent
        }
      }
    }

    // Update image data with cleaned version
    for (let i = 0; i < data.length; i++) {
      data[i] = tempData[i]
    }

    ctx.putImageData(imageData, 0, 0)
  }

  // Helper to get pixel color
  getPixelColor(data, x, y, width) {
    const idx = (y * width + x) * 4
    return {
      r: data[idx],
      g: data[idx + 1],
      b: data[idx + 2],
      a: data[idx + 3],
    }
  }
}

// Export the classes
window.JsBarcode = JsBarcode
window.BarcodeProcessor = BarcodeProcessor
window.SignatureProcessor = SignatureProcessor

