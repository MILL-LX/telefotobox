"use strict";

let socket = io();

window.onload = () => {
   $('#noise').hide();
};

$(function () {

   socket.on('update', (foto) => {
      if(foto != null) {
         $('#noise').hide();
         $('#foto').show();
         $('#foto').attr('src','media/' + foto);
      } else {
         $('#foto').hide();
         $('#noise').show();
      }
   });

   socket.on('noise', () => {
      $('#foto').hide();
      $('#noise').show();
   });

});
