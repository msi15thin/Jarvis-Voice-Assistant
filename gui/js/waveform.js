
let scene, camera, renderer, bars = [];
let state = "idle";
let clock = new THREE.Clock();

const BAR_COUNT = 48;
const RADIUS = 5.5;

function init() {
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 5, 13);
  camera.lookAt(0, 0, 0);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(window.innerWidth, window.innerHeight);
  document.body.appendChild(renderer.domElement);

  scene.add(new THREE.AmbientLight(0x223344, 2));
  const point = new THREE.PointLight(0x00d4ff, 3, 60);
  point.position.set(0, 12, 10);
  scene.add(point);

  const ringGeo = new THREE.TorusGeometry(RADIUS - 0.3, 0.02, 8, 100);
  const ringMat = new THREE.MeshBasicMaterial({ color: 0x114455, transparent: true, opacity: 0.5 });
  const ring = new THREE.Mesh(ringGeo, ringMat);
  ring.rotation.x = Math.PI / 2;
  scene.add(ring);

  for (let i = 0; i < BAR_COUNT; i++) {
    const angle = (i / BAR_COUNT) * Math.PI * 2;
    const geometry = new THREE.BoxGeometry(0.22, 1, 0.22);
    const material = new THREE.MeshStandardMaterial({
      color: 0x00d4ff,
      emissive: 0x0088aa,
      emissiveIntensity: 0.8,
      roughness: 0.3,
      metalness: 0.4
    });
    const bar = new THREE.Mesh(geometry, material);
    bar.position.x = Math.cos(angle) * RADIUS;
    bar.position.z = Math.sin(angle) * RADIUS;
    scene.add(bar);
    bars.push(bar);
  }

  window.addEventListener('resize', onResize);
  animate();
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

function setJarvisState(newState) {
  state = newState;
  const label = document.getElementById('label');
  if (label) label.innerText = newState;
}
window.setJarvisState = setJarvisState;

function animate() {
  requestAnimationFrame(animate);
  const t = clock.getElapsedTime();

  let amplitude, speed, color;
  if (state === "listening") {
    amplitude = 2.4; speed = 6; color = 0x00ff9d;
  } else if (state === "thinking") {
    amplitude = 1.3; speed = 11; color = 0xffaa00;
  } else if (state === "speaking") {
    amplitude = 3.2; speed = 15; color = 0x00d4ff;
  } else {
    amplitude = 0.35; speed = 1.4; color = 0x2a6d9e;
  }

  bars.forEach((bar, i) => {
    const offset = i * 0.35;
    const h = 1 + Math.abs(Math.sin(t * speed + offset)) * amplitude * (0.4 + Math.random() * 0.6);
    bar.scale.y = h;
    bar.position.y = h / 2 - 0.5;
    bar.material.color.setHex(color);
    bar.material.emissive.setHex(color);
  });

  scene.rotation.y = t * 0.12;
  renderer.render(scene, camera);
}

init();