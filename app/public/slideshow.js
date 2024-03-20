"use strict";

let socket = io();

let noise = "noise.gif"

window.onload = () => {
   socket.emit('year', 2020);
};

$(function () {

   socket.on('update', (foto) => {
      if(foto != null) {
         $('#foto').attr('src','media/' + foto);
      } else {
         $('#foto').attr('src',noise);
      }
   });

   socket.on('description', (description) => {
      console.log(description);
      speechSynthesis.speak(new SpeechSynthesisUtterance(description));
   });

});

setInterval(() => {
 socket.emit('next');
}, 3000);
