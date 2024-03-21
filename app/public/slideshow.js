"use strict";

let socket = io();

window.onload = () => {
   $('#noise').hide();
};

$(function () {

   socket.on('update', (foto) => {
      if(foto != null) {
         $('#msg').hide();
         $('#noise').hide();
         $('#foto').show();
         $('#foto').attr('src','media/' + foto);
      } else {
         $('#msg').hide();
         $('#foto').hide();
         $('#noise').show();
      }
   });

   socket.on('noise', () => {
      $('#msg').hide();
      $('#foto').hide();
      $('#noise').show();
   });

   socket.on('msg', (msg) => {
      $("#msg").html("<h1>" + msg + "</h1>");
      $('#msg').hide();
      $('#foto').hide();
      $('#noise').hide();
      $('#msg').show();
   });

});
