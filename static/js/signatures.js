/**
 * E-Signature Tool for Student ID Application
 * Provides functionality for capturing, validating, and saving digital signatures
 */

class SignaturePad {
  constructor(canvasId, options = {}) {
    this.canvas = document.getElementById(canvasId)
    if (!this.canvas) {
      console.error(`Canvas element with id '${canvasId}' not found`)
      return
    }

    this.ctx = this.canvas.getContext("2d")
    this.isDrawing = false
    this.strokes = []
    this.currentStroke = []

    // Default options
    this.options = {
      penColor: options.penColor || "#000000",
      penWidth: options.penWidth || 2,
      backgroundColor: options.backgroundColor || "#ffffff",
      onSave: options.onSave || (() => {}),
      minLength: options.minLength || 100, // Minimum signature length to be valid
    }

    // Set canvas background
    this.setCanvasBackground()

    // Bind events
    this.bindEvents()
  }

  setCanvasBackground() {
    // Fill canvas with background color
    this.ctx.fillStyle = this.options.backgroundColor
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height)
  }

  bindEvents() {
    // Mouse events
    this.canvas.addEventListener("mousedown", this.startDrawing.bind(this))
    this.canvas.addEventListener("mousemove", this.draw.bind(this))
    this.canvas.addEventListener("mouseup", this.stopDrawing.bind(this))
    this.canvas.addEventListener("mouseout", this.stopDrawing.bind(this))

    // Touch events for mobile
    this.canvas.addEventListener("touchstart", this.handleTouchStart.bind(this))
    this.canvas.addEventListener("touchmove", this.handleTouchMove.bind(this))
    this.canvas.addEventListener("touchend", this.stopDrawing.bind(this))
  }

  handleTouchStart(e) {
    e.preventDefault()
    const touch = e.touches[0]
    const mouseEvent = new MouseEvent("mousedown", {
      clientX: touch.clientX,
      clientY: touch.clientY,
    })
    this.canvas.dispatchEvent(mouseEvent)
  }

  handleTouchMove(e) {
    e.preventDefault()
    const touch = e.touches[0]
    const mouseEvent = new MouseEvent("mousemove", {
      clientX: touch.clientX,
      clientY: touch.clientY,
    })
    this.canvas.dispatchEvent(mouseEvent)
  }

  startDrawing(e) {
    this.isDrawing = true
    this.currentStroke = []

    const rect = this.canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left) * (this.canvas.width / rect.width)
    const y = (e.clientY - rect.top) * (this.canvas.height / rect.height)

    this.currentStroke.push({ x, y })
    this.ctx.beginPath()
    this.ctx.moveTo(x, y)
    this.ctx.lineWidth = this.options.penWidth
    this.ctx.lineCap = "round"
    this.ctx.strokeStyle = this.options.penColor
  }

  draw(e) {
    if (!this.isDrawing) return

    const rect = this.canvas.getBoundingClientRect()
    const x = (e.clientX - rect.left) * (this.canvas.width / rect.width)
    const y = (e.clientY - rect.top) * (this.canvas.height / rect.height)

    this.currentStroke.push({ x, y })
    this.ctx.lineTo(x, y)
    this.ctx.stroke()
  }

  stopDrawing() {
    if (this.isDrawing) {
      this.ctx.closePath()
      if (this.currentStroke.length > 0) {
        this.strokes.push([...this.currentStroke])
      }
    }
    this.isDrawing = false
  }

  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    this.setCanvasBackground()
    this.strokes = []
    this.currentStroke = []
  }

  isEmpty() {
    // Check if signature is empty or too short
    let totalLength = 0
    for (const stroke of this.strokes) {
      if (stroke.length > 1) {
        for (let i = 1; i < stroke.length; i++) {
          const dx = stroke[i].x - stroke[i - 1].x
          const dy = stroke[i].y - stroke[i - 1].y
          totalLength += Math.sqrt(dx * dx + dy * dy)
        }
      }
    }
    return totalLength < this.options.minLength
  }

  toDataURL(type = "image/png", quality = 1) {
    // Create a temporary canvas to generate the final image
    const tempCanvas = document.createElement("canvas")
    tempCanvas.width = this.canvas.width
    tempCanvas.height = this.canvas.height
    const tempCtx = tempCanvas.getContext("2d")

    // Fill with transparent background
    tempCtx.clearRect(0, 0, tempCanvas.width, tempCanvas.height)

    // Draw all strokes
    tempCtx.lineWidth = this.options.penWidth
    tempCtx.lineCap = "round"
    tempCtx.strokeStyle = this.options.penColor

    for (const stroke of this.strokes) {
      if (stroke.length > 0) {
        tempCtx.beginPath()
        tempCtx.moveTo(stroke[0].x, stroke[0].y)
        for (let i = 1; i < stroke.length; i++) {
          tempCtx.lineTo(stroke[i].x, stroke[i].y)
        }
        tempCtx.stroke()
        tempCtx.closePath()
      }
    }

    return tempCanvas.toDataURL(type, quality)
  }

  fromDataURL(dataURL) {
    const image = new Image()
    image.src = dataURL
    image.onload = () => {
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
      this.setCanvasBackground()
      this.ctx.drawImage(image, 0, 0, this.canvas.width, this.canvas.height)
    }
  }

  save() {
    if (this.isEmpty()) {
      return { valid: false, message: "Signature is too short or empty" }
    }

    const dataURL = this.toDataURL()
    if (typeof this.options.onSave === "function") {
      this.options.onSave(dataURL)
    }

    return { valid: true, dataURL }
  }
}

// Export the SignaturePad class
window.SignaturePad = SignaturePad

