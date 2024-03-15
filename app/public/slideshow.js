"use strict";

let socket = io();

let noise = "noise.gif"

window.onload = () => {
   socket.emit('year', 2019);
};

$(function () {

   socket.on('update', (foto) => {
      if(foto != null) {
         $('#foto').attr('src','media/' + foto);
      } else {
         $('#foto').attr('src',noise);
      }
   });

});

setInterval(() => {
   console.log('next foto please');
   socket.emit('next');
}, 3000);
