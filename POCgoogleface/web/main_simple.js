// Simple raccoon mask filter - billboard style
let video, scene, camera, renderer, maskMesh;
let faceMesh;

// Alignment parameters
const alignmentParams = {
    offsetX: 0.0,
    offsetY: 0.0,
    offsetZ: 0.0,
    scaleMultiplier: 1.5,
    baseScale: 0.7
};

// Initialize Three.js scene
function initThreeJS() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 1;
    
    renderer = new THREE.WebGLRenderer({
        canvas: document.getElementById('canvas'),
        alpha: true,
        antialias: true
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
}

// Load raccoon mask as a simple textured plane
async function loadMask() {
    try {
        // Try different raccoon image filenames
        let texturePath = 'Raccoon-cartoon.png';
        let response = await fetch(texturePath, { method: 'HEAD' });
        if (!response.ok) {
            texturePath = 'raccoon_transparent.png';
            response = await fetch(texturePath, { method: 'HEAD' });
            if (!response.ok) {
                texturePath = 'racoon_transparent.png';
            }
        }
        
        // Load texture
        const textureLoader = new THREE.TextureLoader();
        const texture = await new Promise((resolve, reject) => {
            textureLoader.load(texturePath, resolve, undefined, reject);
        });
        
        // Create plane geometry (simple flat plane)
        const geometry = new THREE.PlaneGeometry(1, 1);
        
        // Create material with transparent raccoon texture
        const material = new THREE.MeshBasicMaterial({
            map: texture,
            transparent: true,
            side: THREE.DoubleSide,
            alphaTest: 0.1
        });
        
        // Create mesh
        maskMesh = new THREE.Mesh(geometry, material);
        maskMesh.visible = false;
        scene.add(maskMesh);
        
        console.log('✓ Raccoon mask loaded');
        return true;
    } catch (error) {
        console.error('Error loading raccoon mask:', error);
        return false;
    }
}

// Initialize MediaPipe FaceMesh
function initFaceMesh() {
    faceMesh = new FaceMesh({
        locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`
    });
    
    faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: false,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
    
    faceMesh.onResults(onFaceMeshResults);
}

// Handle face detection results
function onFaceMeshResults(results) {
    if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
        if (maskMesh) maskMesh.visible = false;
        updateInfo('No face detected');
        return;
    }
    
    if (!maskMesh) return;
    
    maskMesh.visible = true;
    const landmarks = results.multiFaceLandmarks[0];
    transformMaskToFace(landmarks.map(lm => [lm.x, lm.y, lm.z]));
    updateInfo('Face tracking active');
}

// Transform mask to follow face - SIMPLE BILLBOARD APPROACH
function transformMaskToFace(faceLandmarks) {
    if (!maskMesh || faceLandmarks.length < 468) return;
    
    // Key landmarks
    const nose = faceLandmarks[4];
    const leftEye = faceLandmarks[33];
    const rightEye = faceLandmarks[263];
    const chin = faceLandmarks[152];
    const forehead = faceLandmarks[10];
    
    // Video dimensions
    const videoWidth = video.videoWidth || 1280;
    const videoHeight = video.videoHeight || 720;
    const aspect = videoWidth / videoHeight;
    
    // Convert to 3D coordinates
    function to3D(lm) {
        return {
            x: (lm[0] - 0.5) * alignmentParams.baseScale * aspect,
            y: (0.5 - lm[1]) * alignmentParams.baseScale,
            z: lm[2] * alignmentParams.baseScale * 0.3
        };
    }
    
    const nose3D = to3D(nose);
    const leftEye3D = to3D(leftEye);
    const rightEye3D = to3D(rightEye);
    const chin3D = to3D(chin);
    const forehead3D = to3D(forehead);
    
    // Face center (use nose as primary anchor)
    const faceCenter = {
        x: nose3D.x,
        y: (nose3D.y + (leftEye3D.y + rightEye3D.y) / 2) / 2,
        z: nose3D.z
    };
    
    // Scale based on eye distance
    const eyeDist = Math.sqrt(
        Math.pow(rightEye3D.x - leftEye3D.x, 2) +
        Math.pow(rightEye3D.y - leftEye3D.y, 2)
    );
    const scale = eyeDist * 2.5 * alignmentParams.scaleMultiplier;
    
    // Apply position
    maskMesh.position.set(
        faceCenter.x + alignmentParams.offsetX,
        faceCenter.y + alignmentParams.offsetY,
        faceCenter.z + alignmentParams.offsetZ
    );
    
    // Billboard: always face camera
    maskMesh.rotation.set(0, 0, 0);
    
    // Add roll (head tilt) from eye line
    const eyeAngle = Math.atan2(rightEye3D.y - leftEye3D.y, rightEye3D.x - leftEye3D.x);
    maskMesh.rotation.z = eyeAngle;
    
    // Apply scale
    maskMesh.scale.set(scale, scale, 1);
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

// Initialize camera
async function initCamera() {
    video = document.getElementById('video');
    const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: 1280, height: 720 }
    });
    video.srcObject = stream;
    await video.play();
    
    // Start MediaPipe processing
    const cam = new Camera(video, {
        onFrame: async () => {
            await faceMesh.send({ image: video });
        },
        width: 1280,
        height: 720
    });
    cam.start();
}

// Update info display
function updateInfo(text) {
    document.getElementById('info').textContent = text;
}

// Toggleadjustments panel
function toggleAdjustments() {
    document.getElementById('adjustments').classList.toggle('show');
}

// Update alignment parameters
function updateAlignment(param, value) {
    alignmentParams[param] = parseFloat(value);
    if (param === 'offsetX') document.getElementById('valX').textContent = value;
    if (param === 'offsetY') document.getElementById('valY').textContent = value;
    if (param === 'offsetZ') document.getElementById('valZ').textContent = value;
    if (param === 'scaleMultiplier') document.getElementById('valScale').textContent = value;
}

// Reset alignment
function resetAlignment() {
    alignmentParams.offsetX = 0.0;
    alignmentParams.offsetY = 0.0;
    alignmentParams.offsetZ = 0.0;
    alignmentParams.scaleMultiplier = 1.5;
    
    document.getElementById('offsetX').value = 0.0;
    document.getElementById('offsetY').value = 0.0;
    document.getElementById('offsetZ').value = 0.0;
    document.getElementById('scaleMult').value = 1.5;
    
    updateAlignment('offsetX', 0.0);
    updateAlignment('offsetY', 0.0);
    updateAlignment('offsetZ', 0.0);
    updateAlignment('scaleMultiplier', 1.5);
}

// Initialize everything
async function init() {
    updateInfo('Initializing...');
    initThreeJS();
    await loadMask();
    initFaceMesh();
    await initCamera();
    animate();
    updateInfo('Ready! Look at the camera.');
}

// Start when page loads
window.addEventListener('load', init);

// Handle window resize
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

