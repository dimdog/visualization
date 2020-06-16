import React, { useState, useEffect } from "react";
import * as THREE from 'three';



export const Vis = (props) => {
    // edit these to not have setters
  const renderer = useState(new THREE.WebGLRenderer())[0];
  const camera = useState(new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 3000 ))[0];
  const scene = useState(new THREE.Scene())[0];

  const [circles, setCircles] = useState([{radius: 100, origin:[0, 0, 0], color: "#32a8a4", "id": 1}]);
  const [circleMaterials, setCircleMaterials] = useState({"#32a8a4": new THREE.MeshBasicMaterial({color: "#32a8a4"})});
  const [circleGeometries, setCircleGeometries] = useState({ 50: new THREE.CircleGeometry(50, 128), 100: new THREE.CircleGeometry(100, 256)});
  const [glCircles, setGlCircles] = useState({});

  function getLine(v1, v2, mat){
      var geometry = new THREE.BufferGeometry().setFromPoints( [v1, v2] );
      return new THREE.Line( geometry, mat );
  }
  function getData(){
      fetch("/geometry")
        .then(res => res.json()) // todo fix the bug if the response isn't json parsable
            .then(
                (result) => {
                    if ("circleColors" in result){
                        var newCircleMaterials = { ...circleMaterials };
                        for (const color of result.circleColors){
                            newCircleMaterials[color] = new THREE.MeshBasicMaterial({color: color});
                        }
                        setCircleMaterials(newCircleMaterials);
                    }
                    if ("circles" in result){
                        setCircles(result.circles);
                    }
                    // save lines and handle them
                    //getData(); enable when ready!
                });
  }
  useEffect(() => {
      const newGlCircles = { ...glCircles};
      const existingGlCircles = { ...glCircles};
      var newGeometries = {};
      for (const circle of circles){
          if (circle.id in newGlCircles){
              newGlCircles[circle.id].material = circleMaterials[circle.color];
              delete existingGlCircles[circle.id];
          } else {
              const material = circleMaterials[circle.color];
              if (circle.radius in circleGeometries){
                  const geometry = circleGeometries[circle.radius];
              } else {
                  console.error("NOT IMPLEMENTED");
                  // TODO create Geometry
              }
              newGlCircles[circle.id] = new THREE.Mesh(geometry, material);
              newGlCircles[circle.id].position.set(...circle.origin);
	      scene.add(newGlCircles[circle.id]);
          }
      }
      for (const id of Object.keys(existingGlCircles)){
          scene.remove(existingGlCircles[id]);
      }
      setGlCircles(newGlCircles);
  }, [circles]);
  useEffect(() => {
      renderer.setSize( window.innerWidth, window.innerHeight );
      camera.position.set( 0, 0, 1000 );
      camera.lookAt( 0, 0, 0 );
      document.body.appendChild( renderer.domElement );
      getData();
  }, []);
  useEffect(() => {

      //create a blue LineBasicMaterial
      //var material = new THREE.LineBasicMaterial( { color: 0x0000ff } );
      //const line = getLine(new THREE.Vector3( - 10, 0, 0 ), new THREE.Vector3( 0, 10, 0 ), material);
      //scene.add( line );
      renderer.render( scene, camera );
  });

  return <div />;
  //return <h1>{greeting}</h1>;
}

