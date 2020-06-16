import React, { useState, useEffect } from "react";
import * as THREE from 'three';



export const Vis = (props) => {
  const greeting = 'Hello Function Component!';
  const [circles, setCircles] = useState([{radius: 20, origin:[5,0,0], color: "#32a8a4"}]);
  const [circleMaterials, setCircleMaterials] = useState({"#32a8a4": new THREE.MeshBasicMaterial({color: "#32a8a4"})});

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
                });
  });
  useEffect(() => {
      var renderer = new THREE.WebGLRenderer();
      renderer.setSize( window.innerWidth, window.innerHeight );
      document.body.appendChild( renderer.domElement );

      var camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 500 );
      camera.position.set( 0, 0, 100 );
      camera.lookAt( 0, 0, 0 );

      var scene = new THREE.Scene();
      //create a blue LineBasicMaterial
      var material = new THREE.LineBasicMaterial( { color: 0x0000ff } );
      const line = getLine(new THREE.Vector3( - 10, 0, 0 ), new THREE.Vector3( 0, 10, 0 ), material);
      for (const circle of circles){
          scene.add(getCircle(circle));
      }
      scene.add( line );
      renderer.render( scene, camera );
  });

  return <div />;
  //return <h1>{greeting}</h1>;
}

