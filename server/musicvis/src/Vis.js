import React, { useState, useEffect } from "react";
import * as THREE from 'three';



export const Vis = (props) => {
  const [circles, setCircles] = useState([{radius: 100, origin:[0, 0, 0], color: "#32a8a4"}]);
  const [circleMaterials, setCircleMaterials] = useState({"#32a8a4": new THREE.MeshBasicMaterial({color: "#32a8a4"})});
  const [renderer, setRenderer] = useState(new THREE.WebGLRenderer());
  const [camera, setCamera] = useState(new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 3000 ));
  const [scene, setScene] = useState(new THREE.Scene());

  function getLine(v1, v2, mat){
      var geometry = new THREE.BufferGeometry().setFromPoints( [v1, v2] );
      return new THREE.Line( geometry, mat );
  }
  function getCircle(circle){
      const material = circleMaterials[circle.color];
      const geometry = new THREE.CircleGeometry( circle.radius, 64 );
      const glCircle =  new THREE.Mesh( geometry, material );
      glCircle.position.set( ...circle.origin);
      return glCircle;

  }
  useEffect(() => {
      renderer.setSize( window.innerWidth, window.innerHeight );
      camera.position.set( 0, 0, 2000 );
      camera.lookAt( 0, 0, 0 );
      document.body.appendChild( renderer.domElement );
  }, []);
  useEffect(() => {
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
                        console.log(result);
                        setCircles(result.circles);
                    }
                    // save lines and handle them
                });
  }, []);
  useEffect(() => {

      //create a blue LineBasicMaterial
      //var material = new THREE.LineBasicMaterial( { color: 0x0000ff } );
      //const line = getLine(new THREE.Vector3( - 10, 0, 0 ), new THREE.Vector3( 0, 10, 0 ), material);
      //scene.add( line );
      for (const circle of circles){
          console.log(circle);
          scene.add(getCircle(circle));
      }
      renderer.render( scene, camera );
  });

  return <div />;
  //return <h1>{greeting}</h1>;
}

