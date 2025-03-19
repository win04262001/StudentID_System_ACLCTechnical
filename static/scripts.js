// Function to preview the uploaded image
function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function() {
        const output = document.getElementById('previewImg');
        output.src = reader.result;
    };
    reader.readAsDataURL(event.target.files[0]);
}

// Function to generate barcode
function generateBarcode() {
    const barcodeText = document.getElementById('barcode-input').value;
    const barcodeType = document.getElementById('barcode-type').value;
    const svgElement = document.getElementById('barcode-svg');

    JsBarcode(svgElement, barcodeText, {
        format: barcodeType,
        displayValue: true,
        fontSize: 20,
        lineColor: "#000000",
        width: 2,
        height: 100,
    });

    svgElement.style.display = 'block';
}

// Function to pass the generated barcode to the ID card
function passBarcode() {
    const svgElement = document.getElementById('barcode-svg');
    const barcodePreview = document.getElementById('barcode-preview');

    // Convert SVG to data URL
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();

    img.onload = function() {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        barcodePreview.src = canvas.toDataURL('image/png');
        barcodePreview.style.display = 'block';
    };

    img.src = 'data:image/svg+xml;base64,' + btoa(svgData);
    closeBarcodeModal();
}

// Function to open the barcode modal
function openBarcodeModal() {
    document.getElementById('barcodeModal').style.display = 'block';
}

// Function to close the barcode modal
function closeBarcodeModal() {
    document.getElementById('barcodeModal').style.display = 'none';
}

// Function to handle signature image processing
function passSignature() {
    const canvas = document.getElementById('canvas');
    const signaturePreview = document.getElementById('signature-preview');

    // Convert canvas to data URL
    const dataURL = canvas.toDataURL('image/png');
    signaturePreview.src = dataURL;
    signaturePreview.style.display = 'block';
    closeModal();
}

// Function to open the signature modal
function openModal() {
    document.getElementById('signatureModal').style.display = 'block';
}

// Function to close the signature modal
function closeModal() {
    document.getElementById('signatureModal').style.display = 'none';
}

// Function to download the front ID card as an image
function downloadFront() {
    html2canvas(document.getElementById('front-id-card')).then(canvas => {
        const link = document.createElement('a');
        link.download = 'front-id-card.png';
        link.href = canvas.toDataURL('image/png');
        link.click();
    });
}

// Function to print the front ID card
function printFront() {
    html2canvas(document.getElementById('front-id-card')).then(canvas => {
        const printWindow = window.open('');
        printWindow.document.write('<img src="' + canvas.toDataURL('image/png') + '">');
        printWindow.document.close();
        printWindow.print();
    });
}

// Event listener for image upload
document.getElementById('imageInput').addEventListener('change', function(event) {
    const file = event.target.files[0];
    const reader = new FileReader();

    reader.onload = function(e) {
        const img = new Image();
        img.onload = function() {
            const canvas = document.getElementById('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = img.width;
            canvas.height = img.height;
            ctx.drawImage(img, 0, 0);
        };
        img.src = e.target.result;
    };

    reader.readAsDataURL(file);
});

// Event listener for thickness control
document.getElementById('thickness').addEventListener('input', function() {
    document.getElementById('thicknessValue').textContent = this.value;
});

// Function to remove the background from the signature
function removeBackground(canvas) {
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    // Remove background based on a threshold (not just pure white)
    for (let i = 0; i < data.length; i += 4) {
        const red = data[i];
        const green = data[i + 1];
        const blue = data[i + 2];

        // If the pixel is close to white, make it transparent
        if (red > 200 && green > 200 && blue > 200) {
            data[i + 3] = 0; // Set alpha to 0 (transparent)
        }
    }

    // Put the modified image data back on the canvas
    ctx.putImageData(imageData, 0, 0);
}

// Function to thicken the signature
function thickenSignature(canvas, thickness) {
    const ctx = canvas.getContext('2d');
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const tempCanvas = document.createElement('canvas');
    const tempCtx = tempCanvas.getContext('2d');

    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;
    tempCtx.putImageData(imageData, 0, 0);

    // Clear the original canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw thicker lines
    ctx.lineWidth = thickness;
    ctx.strokeStyle = 'black';
    ctx.drawImage(tempCanvas, 0, 0);
}

// Function to apply changes to the signature
function applySignatureChanges() {
    const afterCanvas = document.getElementById('afterCanvas');
    const signatureImg = document.getElementById('signature-preview-front');
    const thickness = document.getElementById('thicknessSlider').value;

    // Thicken the signature
    thickenSignature(afterCanvas, thickness);

    // Update the signature image with the modified version
    signatureImg.src = afterCanvas.toDataURL();

    // Close the modal
    const signatureToolModal = new bootstrap.Modal(document.getElementById('signatureToolModal'));
    signatureToolModal.hide();
}

// Add click event to the signature image
document.getElementById('signature-preview-front').addEventListener('click', openSignatureTool);

// Function to open the signature tool modal
function openSignatureTool() {
    const signatureImg = document.getElementById('signature-preview-front');
    const beforeCanvas = document.getElementById('beforeCanvas');
    const afterCanvas = document.getElementById('afterCanvas');

    // Set canvas dimensions to match the signature image
    beforeCanvas.width = signatureImg.width;
    beforeCanvas.height = signatureImg.height;
    afterCanvas.width = signatureImg.width;
    afterCanvas.height = signatureImg.height;

    // Draw the original signature on the "before" canvas
    const beforeCtx = beforeCanvas.getContext('2d');
    beforeCtx.drawImage(signatureImg, 0, 0);

    // Draw the signature on the "after" canvas with background removal
    const afterCtx = afterCanvas.getContext('2d');
    afterCtx.drawImage(signatureImg, 0, 0);

    // Remove the background from the "after" canvas
    removeBackground(afterCanvas);

    // Show the modal
    const signatureToolModal = new bootstrap.Modal(document.getElementById('signatureToolModal'));
    signatureToolModal.show();
}