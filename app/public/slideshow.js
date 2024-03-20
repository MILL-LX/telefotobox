"use strict";

let socket = io();

let noise = "noise.gif"

window.onload = () => {
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
