import './style.css'

import * as THREE from 'three';

/* import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { Water } from 'three/addons/objects/Water.js';
import { Sky } from 'three/addons/objects/Sky.js'; */

import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { Water } from 'three/examples/jsm/objects/Water.js';
import { Sky } from 'three/examples/jsm/objects/Sky.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { BooleanKeyframeTrack } from 'three';

let camera, scene, renderer;
let controls, water, sun;
let collected = 0;

const loader = new GLTFLoader();

function random(min, max) {
  return Math.random() * (max - min) + min
}

class Boat {
  constructor(){
    loader.load( 'assets/boat/scene.gltf', ( gltf ) => {
      scene.add( gltf.scene )
      gltf.scene.scale.set( 3, 3, 3 )
      gltf.scene.position.set(5, 13, 50)
      gltf.scene.rotation.y = 1.5

      this.boat = gltf.scene
      this.speed = {
        vel: 0,
        rot: 0
      }
    })
  }

  update () {
    if(this.boat){
      this.boat.rotation.y += this.speed.rot
      this.boat.translateX(this.speed.vel)
    }
  }
}

const boat = new Boat()

class Trash{
  constructor(_scene){
    scene.add( _scene )
    _scene.scale.set( 1.5, 1.5, 1.5 )
    _scene.position.set( random(-100, 100), -.8, random(-100, 100) )

    this.trash = _scene
  }
}

async function loadModel(url) {
  return new Promise((resolve, reject) => {
    loader.load(url, (gltf) => {
      resolve(gltf.scene)
    });
  });
}

let trashModel = null;
async function createTrash() {
  if (!trashModel) {
    trashModel = await loadModel("assets/trash/scene.gltf")
  }
  return new Trash(trashModel.clone())
}

let trashes = []
let TRASH_COUNT = 5
let time = 20
let countDown = 3
let lost = false
let timer
let countdown

init();
animate();
updateCollected();
startCountDown();

async function init() {

  renderer = new THREE.WebGLRenderer();
  renderer.setPixelRatio( window.devicePixelRatio );
  renderer.setSize( window.innerWidth, window.innerHeight );
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  document.body.appendChild( renderer.domElement );

  //

  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera( 55, window.innerWidth / window.innerHeight, 1, 20000 );
  camera.position.set( 60, 60, 200 );

  //

  sun = new THREE.Vector3();

  // Water

  const waterGeometry = new THREE.PlaneGeometry( 10000, 10000 );

  water = new Water(
    waterGeometry,
    {
      textureWidth: 512,
      textureHeight: 512,
      waterNormals: new THREE.TextureLoader().load( 'assets/waternormals.jpg', function ( texture ) {

        texture.wrapS = texture.wrapT = THREE.RepeatWrapping;

      } ),
      sunDirection: new THREE.Vector3(),
      sunColor: 0xffffff,
      waterColor: 0x001e0f,
      distortionScale: 3.7,
      fog: scene.fog !== undefined
    }
  );

  water.rotation.x = - Math.PI / 2;

  scene.add( water );

  // Skybox

  const sky = new Sky();
  sky.scale.setScalar( 10000 );
  scene.add( sky );

  const skyUniforms = sky.material.uniforms;

  skyUniforms[ 'turbidity' ].value = 10;
  skyUniforms[ 'rayleigh' ].value = 2;
  skyUniforms[ 'mieCoefficient' ].value = 0.005;
  skyUniforms[ 'mieDirectionalG' ].value = 0.8;

  const parameters = {
    elevation: 2,
    azimuth: 180
  };

  const pmremGenerator = new THREE.PMREMGenerator( renderer );
  let renderTarget;

  function updateSun() {

    const phi = THREE.MathUtils.degToRad( 90 - parameters.elevation );
    const theta = THREE.MathUtils.degToRad( parameters.azimuth );

    sun.setFromSphericalCoords( 1, phi, theta );

    sky.material.uniforms[ 'sunPosition' ].value.copy( sun );
    water.material.uniforms[ 'sunDirection' ].value.copy( sun ).normalize();

    if ( renderTarget !== undefined ) renderTarget.dispose();

    renderTarget = pmremGenerator.fromScene( sky );

    scene.environment = renderTarget.texture;

  }

  updateSun();

  controls = new OrbitControls( camera, renderer.domElement );
  controls.maxPolarAngle = Math.PI * 0.495;
  controls.target.set( 0, 10, 0 );
  controls.minDistance = 40.0;
  controls.maxDistance = 200.0;
  controls.update();

  const waterUniforms = water.material.uniforms;

  for (let i = 0; i < TRASH_COUNT; i++) {
    trashes.push(await createTrash())
  }

  window.addEventListener( 'resize', onWindowResize );

  window.addEventListener( 'keydown', function(e){
    if (countDown >= 0 || lost) return
    if(e.key === 'ArrowUp'){
      boat.speed.vel = 1
    }
    if(e.key === 'ArrowDown'){
      boat.speed.vel = -1
    }
    if(e.key === 'ArrowLeft'){
      boat.speed.rot = 0.1
    }
    if(e.key === 'ArrowRight'){
      boat.speed.rot = -0.1
    }
  })

  window.addEventListener( 'keyup', function(e) {
    if (e.key === 'ArrowUp' || e.key === 'ArrowDown') boat.speed.vel = 0;
    if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') boat.speed.rot = 0;
  })
}

function onWindowResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize( window.innerWidth, window.innerHeight );
}

async function animate() {
  boat.update();
  requestAnimationFrame( animate );
  render();
  await checkCollisions();
}

function render() {
  water.material.uniforms[ 'time' ].value += 1.0 / 60.0;
  renderer.render( scene, camera );
}

function isColliding(obj1, obj2) {
  return Math.abs(obj1.position.x - obj2.position.x) < 15 && Math.abs(obj1.position.z - obj2.position.z) < 15
}

async function checkCollisions() {
  if (boat.boat) {
    for(let i = 0; i < TRASH_COUNT; i++)
      if (trashes[i] && trashes[i].trash && isColliding(boat.boat, trashes[i].trash)) {
        collected ++
        scene.remove(trashes[i].trash)
        trashes[i].trash = null
        await updateCollected()
      }
  }
}

async function updateCollected() {
  let remaining = TRASH_COUNT - collected
  let u = remaining % 10, d = Math.floor(remaining / 10);
  document.getElementById("n1").src = "assets/numbers/" + d + ".png"
  document.getElementById("n2").src = "assets/numbers/" + u + ".png"
  if (remaining === 0 && !lost) {
    TRASH_COUNT += 5
    trashes = []
    for (let i = 0; i < TRASH_COUNT; i++) {
      trashes.push(await createTrash())
    }
    collected = 0
    await updateCollected()
    time = 21
    updateTimer()
    lost = false
  }
}

function startTimer() {
  timer = setInterval(updateTimer, 1000)
}

function updateTimer() {
  let u = time % 10, d = Math.floor(time / 10);
    if (time === 0) {
      lost = true
      stopTimer()
      document.getElementById("l1").style.display = 'inline-block'
      document.getElementById("l2").style.display = 'inline-block'
      document.getElementById("l3").style.display = 'inline-block'
      document.getElementById("l4").style.display = 'inline-block'
    } else time--;
    document.getElementById("t1").src = "assets/numbers/" + d + ".png"
    document.getElementById("t2").src = "assets/numbers/" + u + ".png"
}

function stopTimer() {
  clearInterval(timer)
}

function startCountDown() {
  let u = time % 10, d = Math.floor(time / 10);
  document.getElementById("t1").src = "assets/numbers/" + d + ".png"
  document.getElementById("t2").src = "assets/numbers/" + u + ".png"
  countdown = setInterval(() => {
    if (countDown === 0) {
      stopCountDown()
      document.getElementById("s1").src = "assets/numbers/g.png"
      document.getElementById("s2").src = "assets/numbers/o.png"
      startTimer()
      setTimeout(() => {
        document.getElementById("s1").style.display = "none"
        document.getElementById("s2").style.display = "none"
      }, 1000)
    } else {
      document.getElementById("s2").src = "assets/numbers/" + countDown + ".png"
    }
    countDown --;
  }, 1000)
}

function stopCountDown() {
  clearInterval(countdown)
}
