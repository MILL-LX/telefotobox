'use strict';

const fs = require('fs');
const express = require('express');
const dotenv = require('dotenv');
const socketIO = require('socket.io');

dotenv.config();

const port = process.env.PORT || '8000';
const media = process.env.MEDIA_PATH;

console.log('loading media from '+ media);

const app = express();
app.use('/', express.static(__dirname + '/public/'));
app.get('/', function (req, res){
   res.sendFile(__dirname + '/public/index.html');
});
app.use("/media/", express.static(process.env.MEDIA_PATH));

const cp_server = app.listen(port, () => console.log('slideshow available at port ' + port));
const cp_socket = socketIO(cp_server);

cp_socket.on('connection', (socket) => {
   console.log('slideshow connected');

   // socket.on('hello', () => {
   //    socket.emit('update', '2019/5391.jpg');
   // });

   socket.on('year', (new_year) => {
      year = new_year;
      console.log('going to year ', year);
      updateFileList();
   });

   socket.on('next', () => {
      if(file_list.length > 0) {
         let i = getRandomInt(file_list.length);
         socket.emit('update', file_list[i]);
         file_list.splice(i, 1);
         if(file_list.length == 0) {
            updateFileList();
         }
      } else {
         console.log('no fotos found');
      }
   });

});

let file_list = [];
let year = null;

function updateFileList() {
   if(year != null) {
      file_list = [];
      fs.readdirSync(media + year).forEach(file => {
         file_list.push(year + '/' + file);
      });
   } else {
      console.log('no year selected');
   }
}

function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}
