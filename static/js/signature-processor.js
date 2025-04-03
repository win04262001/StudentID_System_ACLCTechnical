/**
 * Signature Processor
 * Handles signature processing, background removal, and auto-correction
 */

class SignatureProcessor {
  constructor(canvas) {
    this.canvas = canvas
    this.ctx = canvas.getContext("2d")
    this.tempCanvas = document.createElement("canvas")
    this.tempCtx = this.tempCanvas.getContext("2d")
  }

  /**
   * Remove background from signature
   * Makes white/light pixels transparent
   */
  removeBackground() {
    // Copy canvas content to temp canvas
    this.tempCanvas.width = this.canvas.width
    this.tempCanvas.height = this.canvas.height
    this.tempCtx.drawImage(this.canvas, 0, 0)

    // Get image data
    const imageData = this.tempCtx.getImageData(0, 0, this.tempCanvas.width, this.tempCanvas.height)
    const data = imageData.data

    // Process each pixel
    for (let i = 0; i < data.length; i += 4) {
      const red = data[i]
      const green = data[i + 1]
      const blue = data[i + 2]

      // Check if pixel is light (background)
      if (red > 230 && green > 230 && blue > 230) {
        data[i + 3] = 0 // Set alpha to 0 (transparent)
      }
    }

    // Put processed data back to temp canvas
    this.tempCtx.putImageData(imageData, 0, 0)
    return this.tempCanvas.toDataURL("image/png")
  }

  /**
   * Auto-correct signature
   * Enhances contrast and smooths edges
   */
  autoCorrect() {
    // Copy canvas content to temp canvas
    this.tempCanvas.width = this.canvas.width
    this.tempCanvas.height = this.canvas.height
    this.tempCtx.drawImage(this.canvas, 0, 0)

    // Get image data
    const imageData = this.tempCtx.getImageData(0, 0, this.tempCanvas.width, this.tempCanvas.height)
    const data = imageData.data

    // Process each pixel to enhance contrast
    for (let i = 0; i < data.length; i += 4) {
      const red = data[i]
      const green = data[i + 1]
      const blue = data[i + 2]
      const alpha = data[i + 3]

      // Skip transparent pixels
      if (alpha === 0) continue

      // Calculate grayscale value
      const gray = (red + green + blue) / 3

      // Apply contrast enhancement
      const threshold = 128
      const newValue = gray < threshold ? 0 : 255

      // Set new values
      data[i] = newValue // R
      data[i + 1] = newValue // G
      data[i + 2] = newValue // B
    }

    // Put processed data back to temp canvas
    this.tempCtx.putImageData(imageData, 0, 0)
    return this.tempCanvas.toDataURL("image/png")
  }

  /**
   * Process signature for ID card
   * Removes background and auto-corrects
   */
  processForIDCard() {
    // First remove background
    this.removeBackground()

    // Then auto-correct
    return this.autoCorrect()
  }

  /**
   * Optimize barcode for ID card
   * Ensures the barcode fits properly in the designated area
   */
  optimizeBarcodeForID(barcodeImg) {
    // Create a new canvas for the optimized barcode
    const canvas = document.createElement("canvas")
    const ctx = canvas.getContext("2d")

    // Set canvas size to match the barcode container
    canvas.width = 300 // Standard width for ID card barcode
    canvas.height = 60 // Standard height for ID card barcode

    // Draw the barcode image centered and scaled to fit
    const img = new Image()
    img.src = barcodeImg.src

    // Calculate scaling to fit while maintaining aspect ratio
    const scale = Math.min(canvas.width / img.width, canvas.height / img.height)

    // Calculate centered position
    const x = (canvas.width - img.width * scale) / 2
    const y = (canvas.height - img.height * scale) / 2

    // Draw the scaled and centered barcode
    ctx.drawImage(img, x, y, img.width * scale, img.height * scale)

    return canvas.toDataURL("image/png")
  }
}

// Export for use in other scripts
window.SignatureProcessor = SignatureProcessor

