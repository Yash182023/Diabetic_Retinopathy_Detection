// Theme toggle functionality
const themeToggle = document.getElementById('themeToggle');
const body = document.body;
const toggleIcon = themeToggle.querySelector('i');

// Check for saved theme preference
const savedTheme = localStorage.getItem('theme');
if (savedTheme === 'dark') {
    body.classList.add('dark-mode');
    toggleIcon.classList.replace('fa-moon', 'fa-sun');
}

// Theme toggle event listener
themeToggle.addEventListener('click', () => {
    body.classList.toggle('dark-mode');
    
    // Update icon
    if (body.classList.contains('dark-mode')) {
        toggleIcon.classList.replace('fa-moon', 'fa-sun');
        localStorage.setItem('theme', 'dark');
    } else {
        toggleIcon.classList.replace('fa-sun', 'fa-moon');
        localStorage.setItem('theme', 'light');
    }
});

// File selection handling
document.getElementById('imageUpload').addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : 'No file selected';
    document.getElementById('fileNameDisplay').textContent = fileName;
    
    const uploadArea = document.getElementById('uploadArea');
    if (this.files[0]) {
        uploadArea.classList.add('active');
    } else {
        uploadArea.classList.remove('active');
    }
});

// Drag and drop functionality
const uploadArea = document.getElementById('uploadArea');

uploadArea.addEventListener('dragover', function(e) {
    e.preventDefault();
    this.classList.add('active');
});

uploadArea.addEventListener('dragleave', function() {
    this.classList.remove('active');
});

uploadArea.addEventListener('drop', function(e) {
    e.preventDefault();
    this.classList.remove('active');
    this.classList.add('active');
    
    const file = e.dataTransfer.files[0];
    if (file && file.type.match('image.*')) {
        document.getElementById('imageUpload').files = e.dataTransfer.files;
        document.getElementById('fileNameDisplay').textContent = file.name;
    }
});

// Reset severity indicators
function resetSeverity() {
    for (let i = 0; i < 5; i++) {
        document.getElementById(`severity${i}`).classList.remove('active');
    }
}

// Image upload and prediction
async function uploadImage() {
    let input = document.getElementById("imageUpload");
    let file = input.files[0];
    if (!file) {
        alert("Please select an image.");
        return;
    }

    // Show loading spinner
    document.getElementById('loading').style.display = 'block';
    
    // Hide previous results
    const resultElement = document.getElementById('result');
    resultElement.classList.remove('show');
    
    // Reset severity indicators
    resetSeverity();

    let formData = new FormData();
    formData.append("file", file);

    try {
        let response = await fetch("http://localhost:8000/predict/", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        let result = await response.json();
        
        // Hide loading spinner
        document.getElementById('loading').style.display = 'none';
        
        // Update result text
        document.getElementById('resultText').innerText = 
            `Prediction: ${result.class} (Confidence: ${(result.confidence * 100).toFixed(1)}%)`;
        
        // Animate confidence meter
        const confidenceFill = document.getElementById('confidenceFill');
        confidenceFill.style.width = `${result.confidence * 100}%`;
        
        // Highlight severity level
        const severityClasses = {
            "No DR": 0,
            "Mild": 1,
            "Moderate": 2, 
            "Severe": 3,
            "Proliferative DR": 4
        };
        
        const severityIndex = severityClasses[result.class];
        if (severityIndex !== undefined) {
            document.getElementById(`severity${severityIndex}`).classList.add('active');
        }
        
        // Show result with animation
        resultElement.classList.add('show');
        
    } catch (error) {
        console.error("Error:", error);
        document.getElementById('loading').style.display = 'none';
        alert("An error occurred during prediction. Please try again.");
    }
}