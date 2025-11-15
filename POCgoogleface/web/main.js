// main.js - Real-time raccoon mask with MediaPipe FaceMesh

let scene, camera, renderer, maskMesh, maskTexture;
let faceMesh;
let video;
let maskGeometry;
let maskMaterial;

// Initialize Three.js scene
function initThreeJS() {
    scene = new THREE.Scene();
    
    // Camera matches video dimensions
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    
    renderer = new THREE.WebGLRenderer({ 
        canvas: document.getElementById('canvas'),
        alpha: true,
        antialias: true 
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
}

// Load raccoon mask mesh and texture
async function loadMask() {
    try {
        // Load mesh JSON
        const meshResponse = await fetch('raccoon_mask_mesh.json');
        const meshData = await meshResponse.json();
        
        // Load texture (prefer transparent version, fallback to regular)
        const textureLoader = new THREE.TextureLoader();
        const texturePaths = [
            'raccoon_transparent.png',  // Prefer transparent version
            'raccoon.png', 
            'racoon.png'
        ];
        let textureLoaded = false;
        
        for (const path of texturePaths) {
            try {
                maskTexture = await new Promise((resolve, reject) => {
                    textureLoader.load(
                        path,
                        (texture) => {
                            // Ensure proper transparency handling
                            texture.flipY = false; // Already flipped in Python
                            resolve(texture);
                        },
                        undefined,
                        reject
                    );
                });
                textureLoaded = true;
                console.log(`Loaded texture from: ${path}`);
                break;
            } catch (e) {
                // Try next path
            }
        }
        
        if (!textureLoaded) {
            throw new Error('Could not load raccoon texture');
        }
        
        // Create geometry from mesh data
        maskGeometry = new THREE.BufferGeometry();
        
        const vertices = new Float32Array(meshData.vertices.flat());
        const uvs = new Float32Array(meshData.uv.flat());
        const indices = new Uint16Array(meshData.faces.flat());
        
        maskGeometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
        maskGeometry.setAttribute('uv', new THREE.BufferAttribute(uvs, 2));
        maskGeometry.setIndex(new THREE.BufferAttribute(indices, 1));
        maskGeometry.computeVertexNormals();
        
        // Create material with texture and proper transparency
        maskMaterial = new THREE.MeshBasicMaterial({
            map: maskTexture,
            side: THREE.DoubleSide,
            transparent: true,
            opacity: 1.0,
            alphaTest: 0.1,  // Discard pixels with alpha < 0.1 (removes white background)
            depthWrite: false  // Better transparency rendering
        });
        
        // Create mesh
        maskMesh = new THREE.Mesh(maskGeometry, maskMaterial);
        
        // Center the mesh at origin initially (will be positioned by transform)
        maskGeometry.computeBoundingBox();
        const center = new THREE.Vector3();
        maskGeometry.boundingBox.getCenter(center);
        maskGeometry.translate(-center.x, -center.y, -center.z);
        
        scene.add(maskMesh);
        
        // Initialize mesh properties (preserves 3D raccoon shape)
        initMeshDisplacements();
        
        console.log('Mask loaded:', meshData.vertices.length, 'vertices');
        updateInfo('Mask loaded. Starting face tracking...');
        
        return true;
    } catch (error) {
        console.error('Error loading mask:', error);
        updateInfo('Error loading mask. Check console.');
        return false;
    }
}

// Initialize MediaPipe FaceMesh
function initFaceMesh() {
    faceMesh = new FaceMesh({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
        }
    });
    
    faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: false, // Use 468 points (not 478)
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
    
    faceMesh.onResults(onFaceMeshResults);
}

// Handle MediaPipe results - called every frame when face is detected
function onFaceMeshResults(results) {
    if (!results.multiFaceLandmarks || results.multiFaceLandmarks.length === 0) {
        // No face detected - hide mask
        if (maskMesh) {
            maskMesh.visible = false;
        }
        updateInfo('No face detected. Look at the camera.');
        return;
    }
    
    if (!maskMesh) {
        return; // Mask not loaded yet
    }
    
    // Face detected - show and update mask
    maskMesh.visible = true;
    
    // Get 468 landmarks from first detected face
    const landmarks = results.multiFaceLandmarks[0];
    
    // Convert MediaPipe landmarks to array format
    const facePoints = landmarks.map(lm => [lm.x, lm.y, lm.z]);
    
    // Transform mask to match face in real-time
    transformMaskToFace(facePoints);
    
    updateInfo('Face tracking active - mask following your face!');
}

// Store original mesh (with 3D raccoon shape preserved)
let originalMeshCenter = null;
let meshBounds = null;

// Alignment adjustment parameters (can be tweaked for better fit)
const alignmentParams = {
    offsetX: 0.0,    // Horizontal: positive = right, negative = left
    offsetY: 0.0,    // Vertical: positive = down, negative = up (adjusted for better centering)
    offsetZ: 0.0,     // Depth: positive = forward, negative = back
    scaleMultiplier: 2.0,  // Scale factor (increased default to prevent downscaling)
    baseScale: 0.7    // Base coordinate scale
};

// Initialize: store original mesh properties
function initMeshDisplacements() {
    if (!maskGeometry) return;
    
    // Compute mesh center and bounds to preserve raccoon shape
    const positions = maskGeometry.attributes.position.array;
    const numVertices = positions.length / 3;
    
    let minX = Infinity, maxX = -Infinity;
    let minY = Infinity, maxY = -Infinity;
    let minZ = Infinity, maxZ = -Infinity;
    let sumX = 0, sumY = 0, sumZ = 0;
    
    for (let i = 0; i < numVertices; i++) {
        const x = positions[i * 3];
        const y = positions[i * 3 + 1];
        const z = positions[i * 3 + 2];
        
        sumX += x; sumY += y; sumZ += z;
        minX = Math.min(minX, x); maxX = Math.max(maxX, x);
        minY = Math.min(minY, y); maxY = Math.max(maxY, y);
        minZ = Math.min(minZ, z); maxZ = Math.max(maxZ, z);
    }
    
    originalMeshCenter = [
        sumX / numVertices,
        sumY / numVertices,
        sumZ / numVertices
    ];
    
    meshBounds = {
        width: maxX - minX,
        height: maxY - minY,
        depth: maxZ - minZ
    };
    
    console.log('Mesh bounds:', meshBounds);
}

// Apply rigid transform to position raccoon mask on face (Snapchat-style filter)
// This treats the mask as a rigid 3D object attached to the head pose
function transformMaskToFace(faceLandmarks) {
    if (!maskMesh || faceLandmarks.length < 468) return;
    
    // MediaPipe Face Mesh key landmark indices
    const landmarks = {
        noseTip: 4,
        leftEyeOuter: 33,
        rightEyeOuter: 263,
        leftEyeInner: 133,
        rightEyeInner: 362,
        chin: 152,
        forehead: 10,
        leftCheek: 234,
        rightCheek: 454
    };
    
    // Get video dimensions
    const videoWidth = video.videoWidth || 1280;
    const videoHeight = video.videoHeight || 720;
    const aspect = videoWidth / videoHeight;
    
    // Convert MediaPipe landmarks to 3D coordinates
    // MediaPipe: x[0,1] left->right, y[0,1] top->bottom, z depth (negative=closer)
    // Three.js: x left/right, y up/down, z forward/back (camera looks down -Z)
    function landmarkTo3D(index) {
        const lm = faceLandmarks[index];
        return {
            x: (lm[0] - 0.5) * alignmentParams.baseScale * aspect,
            y: (0.5 - lm[1]) * alignmentParams.baseScale,
            z: -lm[2] * alignmentParams.baseScale * 0.5
        };
    }
    
    // Get key face points for head pose estimation
    const nose = landmarkTo3D(landmarks.noseTip);
    const leftEye = landmarkTo3D(landmarks.leftEyeOuter);
    const rightEye = landmarkTo3D(landmarks.rightEyeOuter);
    const chin = landmarkTo3D(landmarks.chin);
    const forehead = landmarkTo3D(landmarks.forehead);
    
    // ============================================
    // STEP 1: Extract Head Position (Translation T)
    // ============================================
    // Use nose as primary anchor point (most stable)
    const eyeMidpoint = {
        x: (leftEye.x + rightEye.x) / 2,
        y: (leftEye.y + rightEye.y) / 2,
        z: (leftEye.z + rightEye.z) / 2
    };
    
    // Head position: weighted average with nose as primary anchor
    const headPosition = {
        x: nose.x * 0.8 + eyeMidpoint.x * 0.2,
        y: nose.y * 0.7 + eyeMidpoint.y * 0.15 + (forehead.y + chin.y) / 2 * 0.15,
        z: nose.z * 0.8 + eyeMidpoint.z * 0.2
    };
    
    // ============================================
    // STEP 2: Extract Head Orientation (Rotation R)
    // ============================================
    // Build coordinate system from face geometry
    // Right vector: from left eye to right eye (horizontal on face)
    const rightVec = {
        x: rightEye.x - leftEye.x,
        y: rightEye.y - leftEye.y,
        z: rightEye.z - leftEye.z
    };
    
    // Up vector: from chin to forehead (vertical on face)
    const upVec = {
        x: forehead.x - chin.x,
        y: forehead.y - chin.y,
        z: forehead.z - chin.z
    };
    
    // Forward vector: cross product (perpendicular to face plane)
    // forward = right × up
    let forwardVec = {
        x: rightVec.y * upVec.z - rightVec.z * upVec.y,
        y: rightVec.z * upVec.x - rightVec.x * upVec.z,
        z: rightVec.x * upVec.y - rightVec.y * upVec.x
    };
    
    // Normalize forward vector
    const forwardLen = Math.sqrt(forwardVec.x**2 + forwardVec.y**2 + forwardVec.z**2);
    if (forwardLen > 0.001) {
        forwardVec.x /= forwardLen;
        forwardVec.y /= forwardLen;
        forwardVec.z /= forwardLen;
    }
    
    // Ensure forward points toward camera (positive Z in our coordinate system)
    if (forwardVec.z < 0) {
        forwardVec.x = -forwardVec.x;
        forwardVec.y = -forwardVec.y;
        forwardVec.z = -forwardVec.z;
    }
    
    // Recompute right vector as up × forward (orthonormal basis)
    rightVec.x = upVec.y * forwardVec.z - upVec.z * forwardVec.y;
    rightVec.y = upVec.z * forwardVec.x - upVec.x * forwardVec.z;
    rightVec.z = upVec.x * forwardVec.y - upVec.y * forwardVec.x;
    
    // Normalize right vector
    const rightLen = Math.sqrt(rightVec.x**2 + rightVec.y**2 + rightVec.z**2);
    if (rightLen > 0.001) {
        rightVec.x /= rightLen;
        rightVec.y /= rightLen;
        rightVec.z /= rightLen;
    }
    
    // Recompute up vector as forward × right (complete orthonormal basis)
    upVec.x = forwardVec.y * rightVec.z - forwardVec.z * rightVec.y;
    upVec.y = forwardVec.z * rightVec.x - forwardVec.x * rightVec.z;
    upVec.z = forwardVec.x * rightVec.y - forwardVec.y * rightVec.x;
    
    // Normalize up vector
    const upLen = Math.sqrt(upVec.x**2 + upVec.y**2 + upVec.z**2);
    if (upLen > 0.001) {
        upVec.x /= upLen;
        upVec.y /= upLen;
        upVec.z /= upLen;
    }
    
    // Convert rotation matrix to Euler angles for Three.js
    // Simplified: only use yaw and pitch to keep mask facing camera
    // When head turns right, we want mask to turn right too
    const yaw = Math.atan2(-forwardVec.x, forwardVec.z);
    const pitch = Math.asin(forwardVec.y);
    const roll = Math.atan2(rightVec.y, Math.sqrt(rightVec.x**2 + rightVec.z**2));
    
    // ============================================
    // STEP 3: Extract Head Size (Scale S)
    // ============================================
    // Use eye distance as reference for head size
    const eyeDist = Math.sqrt(
        Math.pow(rightEye.x - leftEye.x, 2) +
        Math.pow(rightEye.y - leftEye.y, 2) +
        Math.pow(rightEye.z - leftEye.z, 2)
    );
    
    // Scale mask to match head size
    const targetWidth = eyeDist * 3.5 * alignmentParams.scaleMultiplier;
    let scale = meshBounds ? (targetWidth / meshBounds.width) : 1.0;
    
    // Clamp scale
    const minScale = 0.5;
    const maxScale = 5.0;
    scale = Math.max(minScale, Math.min(maxScale, scale));
    
    // ============================================
    // STEP 4: Apply Rigid Transform to Mask
    // ============================================
    // Apply translation (head position)
    maskMesh.position.set(
        headPosition.x + alignmentParams.offsetX,
        headPosition.y + alignmentParams.offsetY,
        headPosition.z + alignmentParams.offsetZ
    );
    
    // Make mask face the camera (billboard effect) but positioned at head
    // This ensures the mask is never orthogonal to view
    maskMesh.lookAt(0, 0, 0);
    
    // Apply head tilt (roll)
    maskMesh.rotateZ(roll);
    
    // Apply scale (head size)
    maskMesh.scale.set(scale, scale, scale);
    
    // The mask geometry itself is NOT deformed - it's just transformed as a rigid body
}


// Update info display
function updateInfo(text) {
    document.getElementById('info').textContent = text;
}

// Toggle adjustments panel
function toggleAdjustments() {
    const panel = document.getElementById('adjustments');
    panel.classList.toggle('show');
}

// Update alignment parameters
function updateAlignment(param, value) {
    alignmentParams[param] = parseFloat(value);
    
    // Update display
    if (param === 'offsetX') document.getElementById('valX').textContent = value;
    if (param === 'offsetY') document.getElementById('valY').textContent = value;
    if (param === 'offsetZ') document.getElementById('valZ').textContent = value;
    if (param === 'scaleMultiplier') document.getElementById('valScale').textContent = value;
}

// Reset alignment to defaults
function resetAlignment() {
    alignmentParams.offsetX = 0.0;
    alignmentParams.offsetY = 0.0;
    alignmentParams.offsetZ = 0.0;
    alignmentParams.scaleMultiplier = 2.0;
    
    document.getElementById('offsetX').value = 0.0;
    document.getElementById('offsetY').value = 0.0;
    document.getElementById('offsetZ').value = 0.0;
    document.getElementById('scaleMult').value = 2.0;
    
    updateAlignment('offsetX', 0.0);
    updateAlignment('offsetY', 0.0);
    updateAlignment('offsetZ', 0.0);
    updateAlignment('scaleMultiplier', 2.0);
}

// Initialize camera
async function initCamera() {
    video = document.getElementById('video');
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { 
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user' // Front-facing camera
            }
        });
        video.srcObject = stream;
        
        video.onloadedmetadata = () => {
            // Update camera aspect ratio to match video
            const aspect = video.videoWidth / video.videoHeight;
            camera.aspect = aspect;
            camera.updateProjectionMatrix();
            
            // Position camera to overlay mask on face
            camera.position.set(0, 0, 1.5); // Adjust Z to match face size
            camera.lookAt(0, 0, 0);
            
            // Start MediaPipe processing
            const cameraUtil = new Camera(video, {
                onFrame: async () => {
                    await faceMesh.send({ image: video });
                },
                width: video.videoWidth,
                height: video.videoHeight
            });
            cameraUtil.start();
            
            updateInfo('Camera started. Face tracking active - mask will follow your face!');
        };
    } catch (error) {
        console.error('Error accessing camera:', error);
        updateInfo('Error accessing camera. Check permissions.');
    }
}

// Animation loop - renders mask overlay in real-time
function animate() {
    requestAnimationFrame(animate);
    
    if (renderer && scene && camera) {
        // Update renderer size to match window
        renderer.setSize(window.innerWidth, window.innerHeight);
        
        // Render mask overlay on top of video
        renderer.render(scene, camera);
    }
}

// Handle window resize
window.addEventListener('resize', () => {
    if (camera && renderer) {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    }
});

// Initialize everything
async function init() {
    updateInfo('Initializing...');
    
    initThreeJS();
    initFaceMesh();
    
    const maskLoaded = await loadMask();
    if (!maskLoaded) {
        return;
    }
    
    await initCamera();
    animate();
}

// Start when page loads
window.addEventListener('load', init);

