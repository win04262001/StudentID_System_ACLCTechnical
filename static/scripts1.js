// Front ID Card Scripts
function previewPhoto() {
    const file = document.getElementById("photo-upload").files[0];
    const reader = new FileReader();
    const preview = document.getElementById("photo-preview");
    const indicator = document.getElementById("photo-indicator");

    if (file && file.type.startsWith('image/')) {
        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = "block";
            indicator.style.display = "none";

            preview.onload = function () {
                console.log("Photo loaded successfully");
            };
        };
        reader.readAsDataURL(file);
    } else {
        alert("Please upload a valid image file.");
    }
}

// Track the currently selected element (barcode or signature)
let selectedElement = null;

// Function to select an element (barcode or signature)
function selectElement(elementType) {
    selectedElement = elementType;
    // Remove selection from all elements
    document.querySelectorAll('.barcode-container, .signature-container').forEach(el => el.classList.remove('selected'));
    // Add selection to the clicked element
    if (elementType === 'barcode') {
        document.getElementById('barcode-container').classList.add('selected');
    } else if (elementType === 'signature') {
        document.getElementById('signature-container').classList.add('selected');
    }
}

// Make the barcode draggable and resizable
const barcodePreview = document.getElementById('barcode-preview');
const barcodeContainer = document.getElementById('barcode-container');
const barcodeResizeHandle = document.getElementById('barcode-resize-handle');

let isBarcodeDragging = false;
let isBarcodeResizing = false;
let barcodeOffsetX, barcodeOffsetY;

// Dragging functionality
barcodePreview.addEventListener('mousedown', (e) => {
    if (!isBarcodeResizing && selectedElement === 'barcode') {
        isBarcodeDragging = true;
        barcodeOffsetX = e.clientX - barcodePreview.getBoundingClientRect().left;
        barcodeOffsetY = e.clientY - barcodePreview.getBoundingClientRect().top;
        barcodePreview.style.cursor = 'grabbing';
    }
});

// Resizing functionality
barcodeResizeHandle.addEventListener('mousedown', (e) => {
    if (selectedElement === 'barcode') {
        isBarcodeResizing = true;
        e.stopPropagation(); // Prevent dragging while resizing
    }
});

// Make the signature draggable and resizable
const signaturePreview = document.getElementById('signature-preview');
const signatureContainer = document.getElementById('signature-container');
const resizeHandle = document.getElementById('resize-handle');

let isDragging = false;
let isResizing = false;
let offsetX, offsetY;

// Dragging functionality
signaturePreview.addEventListener('mousedown', (e) => {
    if (!isResizing && selectedElement === 'signature') {
        isDragging = true;
        offsetX = e.clientX - signaturePreview.getBoundingClientRect().left;
        offsetY = e.clientY - signaturePreview.getBoundingClientRect().top;
        signaturePreview.style.cursor = 'grabbing';
    }
});

// Resizing functionality
resizeHandle.addEventListener('mousedown', (e) => {
    if (selectedElement === 'signature') {
        isResizing = true;
        e.stopPropagation(); // Prevent dragging while resizing
    }
});

// Handle mouse movements for both barcode and signature
document.addEventListener('mousemove', (e) => {
    if (isBarcodeDragging && selectedElement === 'barcode') {
        const containerRect = barcodeContainer.getBoundingClientRect();
        const x = Math.max(0, Math.min(containerRect.width - barcodePreview.offsetWidth, e.clientX - barcodeOffsetX - containerRect.left));
        const y = Math.max(0, Math.min(containerRect.height - barcodePreview.offsetHeight, e.clientY - barcodeOffsetY - containerRect.top));
        barcodePreview.style.left = `${x}px`;
        barcodePreview.style.top = `${y}px`;
    } else if (isBarcodeResizing && selectedElement === 'barcode') {
        const containerRect = barcodeContainer.getBoundingClientRect();
        const width = Math.max(50, Math.min(containerRect.width, e.clientX - containerRect.left));
        const height = Math.max(50, Math.min(containerRect.height, e.clientY - containerRect.top));
        barcodePreview.style.width = `${width}px`;
        barcodePreview.style.height = `${height}px`;
    }

    if (isDragging && selectedElement === 'signature') {
        const containerRect = signatureContainer.getBoundingClientRect();
        const x = Math.max(0, Math.min(containerRect.width - signaturePreview.offsetWidth, e.clientX - offsetX - containerRect.left));
        const y = Math.max(0, Math.min(containerRect.height - signaturePreview.offsetHeight, e.clientY - offsetY - containerRect.top));
        signaturePreview.style.left = `${x}px`;
        signaturePreview.style.top = `${y}px`;
    } else if (isResizing && selectedElement === 'signature') {
        const containerRect = signatureContainer.getBoundingClientRect();
        const width = Math.max(50, Math.min(containerRect.width, e.clientX - containerRect.left));
        const height = Math.max(50, Math.min(containerRect.height, e.clientY - containerRect.top));
        signaturePreview.style.width = `${width}px`;
        signaturePreview.style.height = `${height}px`;
    }
});

// Reset dragging and resizing states
document.addEventListener('mouseup', () => {
    isBarcodeDragging = false;
    isBarcodeResizing = false;
    isDragging = false;
    isResizing = false;
    barcodePreview.style.cursor = 'grab';
    signaturePreview.style.cursor = 'grab';
});

// Barcode Generator Scripts
function openBarcodeModal() {
    document.getElementById('barcodeModal').style.display = 'flex';
}

function closeBarcodeModal() {
    document.getElementById('barcodeModal').style.display = 'none';
}

function generateBarcode() {
    const barcodeInput = document.getElementById('barcode-input').value.trim();
    const barcodeType = document.getElementById('barcode-type').value;
    const barcodeSvg = document.getElementById('barcode-svg');

    if (barcodeInput) {
        barcodeSvg.innerHTML = '';
        JsBarcode(barcodeSvg, barcodeInput, {
            format: barcodeType,
            displayValue: true,
            fontSize: 16,
        });
        barcodeSvg.style.display = 'block';
    } else {
        alert('Please enter barcode text.');
    }
}

function passBarcode() {
    const barcodeSvg = document.getElementById('barcode-svg');
    const barcodePreview = document.getElementById('barcode-preview');
    const barcodeIndicator = document.getElementById('barcode-indicator');

    if (barcodeSvg.style.display === 'block') {
        const svgData = new XMLSerializer().serializeToString(barcodeSvg);
        const dataUrl = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svgData);

        barcodePreview.src = dataUrl;
        barcodePreview.style.display = 'block';
        barcodeIndicator.style.display = 'none';

        closeBarcodeModal();
    } else {
        alert('Please generate a barcode first.');
    }
}

// Signature Tool Modal Scripts
const modal = document.getElementById('signatureModal');
const imageInput = document.getElementById('imageInput');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const thicknessInput = document.getElementById('thickness');
const thicknessValue = document.getElementById('thicknessValue');
const downloadBtn = document.getElementById('downloadBtn');

let originalImageData = null;

function openModal() {
    modal.style.display = 'flex';
}

function closeModal() {
    modal.style.display = 'none';
}

imageInput.addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (event) {
            const img = new Image();
            img.onload = function () {
                canvas.width = img.width;
                canvas.height = img.height;
                ctx.drawImage(img, 0, 0);

                // Save the original image data
                originalImageData = ctx.getImageData(0, 0, canvas.width, canvas.height);

                // Process the image
                processImage();
            };
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    }
});

thicknessInput.addEventListener('input', function () {
    thicknessValue.textContent = thicknessInput.value;
    if (originalImageData) {
        processImage();
    }
});

downloadBtn.addEventListener('click', function () {
    const link = document.createElement('a');
    link.download = 'signature.png';
    link.href = canvas.toDataURL('image/png');
    link.click();
});

function processImage() {
    ctx.putImageData(originalImageData, 0, 0);
    removeBackground();
    enhanceSignature();
    adjustThickness(thicknessInput.value);
}

function removeBackground() {
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const threshold = 200;

    for (let i = 0; i < data.length; i += 4) {
        const r = data[i];
        const g = data[i + 1];
        const b = data[i + 2];

        if (r > threshold && g > threshold && b > threshold) {
            data[i + 3] = 0;
        }
    }

    ctx.putImageData(imageData, 0, 0);
}

function enhanceSignature() {
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;
    const contrast = 1.5;
    const brightness = -50;

    for (let i = 0; i < data.length; i += 4) {
        if (data[i + 3] !== 0) {
            data[i] = contrast * (data[i] - 128) + 128 + brightness;
            data[i + 1] = contrast * (data[i + 1] - 128) + 128 + brightness;
            data[i + 2] = contrast * (data[i + 2] - 128) + 128 + brightness;

            data[i] = Math.min(255, Math.max(0, data[i]));
            data[i + 1] = Math.min(255, Math.max(0, data[i + 1]));
            data[i + 2] = Math.min(255, Math.max(0, data[i + 2]));
        }
    }

    ctx.putImageData(imageData, 0, 0);
}

function adjustThickness(thickness) {
    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const data = imageData.data;

    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = canvas.width;
    tempCanvas.height = canvas.height;
    const tempCtx = tempCanvas.getContext('2d');

    tempCtx.putImageData(imageData, 0, 0);

    ctx.lineWidth = thickness;
    ctx.strokeStyle = 'black';
    ctx.globalCompositeOperation = 'source-over';

    for (let i = 0; i < data.length; i += 4) {
        if (data[i + 3] !== 0) {
            const x = (i / 4) % canvas.width;
            const y = Math.floor((i / 4) / canvas.width);

            ctx.beginPath();
            ctx.arc(x, y, thickness / 2, 0, Math.PI * 2);
            ctx.stroke();
        }
    }
}

// Function to check if the signature is present and hide the indicator
function checkSignature() {
    const signaturePreview = document.getElementById('signature-preview');
    const signatureIndicator = document.getElementById('signature-indicator');

    if (signaturePreview.style.display === 'block') {
        signatureIndicator.style.display = 'none';
    } else {
        signatureIndicator.style.display = 'block';
    }
}

// Pass Signature to Front ID Card
function passSignature() {
    const signaturePreview = document.getElementById('signature-preview');
    const signatureDataURL = canvas.toDataURL('image/png');

    if (signatureDataURL !== "data:,") {
        signaturePreview.src = signatureDataURL;
        signaturePreview.style.display = 'block';
        checkSignature();
        closeModal();
    } else {
        alert('Please create a signature first.');
    }
}

// Download and Print Functions
function downloadFront() {
    const frontCard = document.querySelector("#front-id-card");
    if (frontCard.innerHTML.trim() !== "") {
        html2canvas(frontCard, {
            scale: 2,
            useCORS: true,
            allowTaint: true,
            logging: true,
            quality: 1
        }).then(canvas => {
            const link = document.createElement("a");
            link.download = "id-card-front.png";
            link.href = canvas.toDataURL("image/png", { quality: 1 });
            link.click();
        });
    } else {
        alert('The front ID card is empty.');
    }
}

function printFront() {
    const frontCard = document.getElementById("front-id-card").cloneNode(true);
    if (frontCard.innerHTML.trim() !== "") {
        const printWindow = window.open('', '_blank');
        printWindow.document.body.appendChild(frontCard);
        printWindow.document.write('<script>window.onload = function() { window.print(); window.close(); }<\/script>');
        printWindow.document.close();
    } else {
        alert('The front ID card is empty.');
    }
}

// Initialize on page load
window.onload = function () {
    checkSignature();
};