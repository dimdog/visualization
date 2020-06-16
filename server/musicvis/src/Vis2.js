import React, { useState, useEffect } from "react";
import * as THREE from 'three';

class Vis extends React.Component {
    constructor(props){
        super(props);
        this.renderer = new THREE.WebGLRenderer();
        this.camera = new THREE.PerspectiveCamera( 45, window.innerWidth / window.innerHeight, 1, 3000 );
        this.scene = new THREE.Scene();
        this.state = {
            circles: [{radius: 100, origin:[0, 0, 0], color: "#32a8a4", "id": 1}],
            circleMaterials: {"#32a8a4": new THREE.MeshBasicMaterial({color: "#32a8a4"})},
            circleGeometries: { 50: new THREE.CircleGeometry(50, 128), 100: new THREE.CircleGeometry(100, 256)},
            glCircles: {},
            rays: [{p1: [0,0,0], p2:[100,100,0], color: '#fa0000', id:1}],
            rayMaterials: {'#fa0000': new THREE.LineBasicMaterial( { color: '#fa0000' }) },
            glRays: {},
            shouldUpdate: true
        };
        this.getData = this.getData.bind(this);
        this.drawCircles = this.drawCircles.bind(this);
        this.drawRays = this.drawRays.bind(this);
    }
    componentDidMount(){
        this.renderer.setSize( window.innerWidth, window.innerHeight );
        this.camera.position.set( 0, 0, 1000 );
        this.camera.lookAt( 0, 0, 0 );
        document.body.appendChild( this.renderer.domElement );
        this.getData();
    }
    shouldComponentUpdate(){
        return this.state.shouldUpdate;
    }
    getData(){
      fetch("/geometry")
        .then(res => res.json()) // todo fix the bug if the response isn't json parsable
            .then(
                (result) => {
                    var updateObj = {shouldUpdate: false};
                    if ("circleColors" in result){
                        var newCircleMaterials = { ...this.state.circleMaterials };
                        for (const color of result.circleColors){
                            newCircleMaterials[color] = new THREE.MeshBasicMaterial({color: color});
                        }
                        updateObj.circleMaterials = newCircleMaterials;
                    }
                    if ("lineColors" in result){
                        var newRayMaterials = { ...this.state.rayMaterials };
                        for (const color of result.lineColors){
                            newRayMaterials[color] = new THREE.LineBasicMaterial({color: color});
                        }
                        updateObj.rayMaterials = newRayMaterials;
                    }
                    if ("circles" in result){
                        updateObj.circles = result.circles;
                    }
                    if ("rays" in result){
                        updateObj.rays = result.rays;
                    }
                    this.setState(updateObj, () => {
                        this.drawCircles();
                        this.drawRays();
                        this.renderer.render( this.scene, this.camera );
                    });
                    this.getData();
                });
    }
    drawRays(){
      const newGlRays = { ...this.state.glRays};
      const existingGlRays = { ...this.state.glRays};
      for (const ray of this.state.rays){
          if (ray.id in newGlRays){
              newGlRays[ray.id].geometry.setFromPoints([new THREE.Vector3(...ray.p1), new THREE.Vector3(...ray.p2)]);
              delete existingGlRays[ray.id];
          } else {
              const material = this.state.rayMaterials[ray.color];
              const geometry = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...ray.p1), new THREE.Vector3(...ray.p2)]);
              newGlRays[ray.id] = new THREE.Line(geometry, material);
	      this.scene.add(newGlRays[ray.id]);
          }
      }
      for (const id of Object.keys(existingGlRays)){
          this.scene.remove(existingGlRays[id]);
      }
      this.setState({glRays: newGlRays});
    }
    drawCircles(){
      const newGlCircles = { ...this.state.glCircles};
      const existingGlCircles = { ...this.state.glCircles};
      var newGeometries = {};
      for (const circle of this.state.circles){
          if (circle.id in newGlCircles){
              newGlCircles[circle.id].material = this.state.circleMaterials[circle.color];
              delete existingGlCircles[circle.id];
          } else {
              const material = this.state.circleMaterials[circle.color];
              if (circle.radius in this.state.circleGeometries){
                  const geometry = this.state.circleGeometries[circle.radius];
                  newGlCircles[circle.id] = new THREE.Mesh(geometry, material);
                  newGlCircles[circle.id].position.set(...circle.origin);
                  this.scene.add(newGlCircles[circle.id]);
              } else {
                  console.error("NOT IMPLEMENTED");
                  // TODO create Geometry
              }
          }
      }
      for (const id of Object.keys(existingGlCircles)){
          this.scene.remove(existingGlCircles[id]);
      }
      this.setState({glCircles: newGlCircles});
    }
    render(){
        return <div />;
    }
}
export default Vis;
