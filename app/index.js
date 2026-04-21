'use strict';

const fs = require('fs');
const express = require('express');
const dotenv = require('dotenv');
const util = require('util');
const exec = util.promisify(require('child_process').exec);

// for comminicating with browser client
const socketIO = require('socket.io');

// for reading foto metadata
const ExifReader = require('exifreader');

// load any environment variables from our .env file
dotenv.config();

const min_year = process.env.MIN_YEAR || '2014';
const max_year = process.env.MAX_YEAR || '2026';
const foto_delay = process.env.FOTO_DELAY || '10000';

console.log('min_year =', min_year);
console.log('max_year =', max_year);
console.log('foto_delay =', foto_delay);

// 1 = phone on hook
// 0 = phone off hook
let hook_status = 1;

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

   socket.on('hook', (new_hook_status) => {
      hook_status = new_hook_status;
      console.log('hook status:', hook_status);
      if(hook_status == 1) {
         clearInterval(foto_timer);
         io.emit('noise');
         killSpeech();
      } else {
         welcomeMessage();
      }
   });

   socket.on('year', (new_year) => {
      console.log('chosen year: '+ new_year);
      if(hook_status == 0) {
         io.emit('msg', new_year);
         killSpeech();
         setTimeout(()=>{
            goToYear(new_year);
         }, 500);
      } else {
         io.emit('sorry, phone is on the hook');
         console.log('cant go to', new_year, ', phone on hook');
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
let foto_timer = null;

async function goToYear(new_year) {

   await exec('sudo -i -u pi spd-say -w "going to the year' + new_year + '"');

   if(new_year >= min_year && new_year <= max_year) {

      year = new_year;
      console.log('going to year ', year);
      updateFileList();
      clearInterval(foto_timer);
      nextFoto();
      foto_timer = setInterval(nextFoto, foto_delay);
      
   } else {

      console.log("no media for year", new_year);
      io.emit('noise');
      clearInterval(foto_timer);
      foto_timer = null;
      if(new_year < max_year) {
         exec('sudo -i -u pi spd-say -w "sorry, I don\'t have any photos from' + new_year + '"');
      } else {
         exec('sudo -i -u pi spd-say -w "' + new_year + ' is in the future. sorry, I don\'t have any photos from the future."');
      }
   }
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
   let descriptions = tags.UserComment && tags.UserComment.description ? Object.values(JSON.parse(tags.UserComment.description)) : new Array('sorry, no description available', undefined, 'computer says no');
   //let i = getRandomInt(descriptions.length);
   //io.emit('description', descriptions[i]);
   
   for (let i = descriptions.length-1; i >= 0; i--) {
      descriptions[i] = descriptions[i].replace(/[\\$'"]/g, "\\$&")
   }
   //exec('spd-say "' + descriptions[i] + '"');
   //console.log(descriptions);
   await exec('sudo -i -u pi spd-say -w "' + descriptions[0] + '"');
   await exec('sudo -i -u pi spd-say -w "' + descriptions[1] + '"');
   await exec('sudo -i -u pi spd-say -w "' + descriptions[2] + '"');
}

async function welcomeMessage() {
   await exec('sudo -i -u pi cvlc dialtone.mp3 --play-and-exit');
   if(hook_status == 0) {
      exec('sudo -i -u pi spd-say "welcome to the MILL tele photo slideshow machine. please dial the year you would like to travel to"');
   }
}

function killSpeech() {
   // try {
      exec('sudo pkill -f speech-dispatch',(error) => {});
   // } catch(err) {}
}


// ------------------------------------------------------------------------- //
// utilities
// ------------------------------------------------------------------------- //

function getRandomInt(max) {
   return Math.floor(Math.random() * max);
}