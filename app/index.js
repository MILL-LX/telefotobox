'use strict';

const fs = require('fs');
const express = require('express');
const dotenv = require('dotenv');
const exec = require('child_process').exec;

// for comminicating with browser client
const socketIO = require('socket.io');

// for reading foto metadata
const ExifReader = require('exifreader');

// load any environment variables from our .env file
dotenv.config();

const min_year = process.env.MIN_YEAR || '2019';
const max_year = process.env.MAX_YEAR || '2023';
const foto_delay = process.env.FOTO_DELAY || '3000';


// ------------------------------------------------------------------------- //
// web server 
// ------------------------------------------------------------------------- //

const port = process.env.PORT || '8000';
const media = process.env.MEDIA_PATH;
console.log('loading media from '+ media);

const app = express();
app.use('/', express.static(__dirname + '/public/'));
app.get('/', function (req, res){
   res.sendFile(__dirname + '/public/index.html');
});
app.use("/media/", express.static(process.env.MEDIA_PATH));

const server = app.listen(port, () => console.log('slideshow available at port ' + port));


// ------------------------------------------------------------------------- //
// socket connections
// ------------------------------------------------------------------------- //

const io = socketIO(server);

io.on('connection', (socket) => {
   console.log('client connected');

   socket.on('hello', () => {
      socket.emit('howdy');
   });

   socket.on('dialer_ready', () => {
      console.log('dialer is ready');
      io.emit('noise');
   });

   socket.on('hook', (hook_status) => {
      console.log('hook status:', hook_status);
      if(hook_status == 1) {
         clearInterval(foto_timer);
         io.emit('noise');
      } else {

      }
   });

   socket.on('year', (new_year) => {
      if(new_year >= min_year && new_year < max_year) {
         goToYear(new_year);
      } else {
         console.log("no media for year", new_year);
      }
   });

   socket.on('next', () => {
      nextFoto();
   });

});


// ------------------------------------------------------------------------- //
// slideshow
// ------------------------------------------------------------------------- //

let file_list = [];
let year = null;
let foto_timer;

function goToYear(new_year) {
   year = new_year;
   console.log('going to year ', year);
   updateFileList();
   clearInterval(foto_timer);
   nextFoto();
   foto_timer = setInterval(nextFoto, foto_delay);
}

function nextFoto() {
   if(file_list.length > 0) {
      let i = getRandomInt(file_list.length);
      io.emit('update', file_list[i]);
      readExif(media + file_list[i]);
      file_list.splice(i, 1);
      if(file_list.length == 0) {
         updateFileList();
      }
   } else {
      console.log('no fotos found');
   }
}

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

async function readExif(file) {
   const tags = await ExifReader.load(file);
   let descriptions = Object.values(JSON.parse(tags.UserComment.description));
   let i = getRandomInt(descriptions.length);
   io.emit('description', descriptions[i]);
}


// ------------------------------------------------------------------------- //
// utilities
// ------------------------------------------------------------------------- //

function getRandomInt(max) {
   return Math.floor(Math.random() * max);
}