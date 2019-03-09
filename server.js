// ****************************************************************************
// This node script runs a http-server, serving a mobile website that can
// be used to record a voice message which will be uploaded and saved.
// The server creates thereafter the metadata for the voice message and
// passes them to another programm (printer/voiceMsgGenerator.py) to print it.
//
// Written by Andre Fritzinger
//
// ****************************************************************************
// Required packages:
// npm install express multer node-cmd wav-file-info body-parser

const express = require('express'); // use express to run the webserver
const app = express();
const port = 3000;
const multer  = require('multer') // use multer to upload blob data
const upload = multer(); // set multer to be the upload variable
const fs = require('fs'); // use the file system so we can save files
const cmd = require('node-cmd'); // use the console to run the "voiceMsgGenerator.py" pythonscript
const wavFileInfo = require('wav-file-info'); // use wavFileInfo to determine the voice message duration
const bodyParser = require('body-parser'); // use bodyparser to parse the json
var barcodeData, name, date, length;
var uploadDirectory = __dirname + '/public/uploads/' + getDateFormated('short') + '/'; // where to save the file

app.use(bodyParser.json());

// Get the voice message creators name
app.post('/name', function (req, res, next) {
  name = '"' + req.body.name + '"';
  res.sendStatus(200); //send back that everything went ok
  console.log("\nNew voicemsg");
  console.log(name);
})

// Save the recieved voice message to the "public/uploads" folder
app.post('/upload', upload.single('soundBlob'), function (req, res, next) {
  fs.mkdir(uploadDirectory, { recursive: true }, (err) => { // Make a new directory with the current date
      if (err) throw err;
  });
  let uploadPath = uploadDirectory + req.file.originalname
  fs.writeFileSync(uploadPath, Buffer.from(new Uint8Array(req.file.buffer))); // write the blob to the server as a file
  res.sendStatus(200); //send back that everything went ok

  barcodeData = req.file.originalname.replace('.wav',''); // get the filename to pass it later as the barcode data
  console.log(barcodeData);
  date = getDateFormated();

  // Get the voice message duration
  var promise = new Promise(function(resolve, reject) {
    wavFileInfo.infoByFilename(uploadPath, function(err, info){ // load the wavFileInfo of the saved soundfile
      if (err)throw err;
      else{
        resolve();
        length=[0,0];
        length[0] = Math.floor(Math.round(info.duration) / 60);
        length[1] = Math.round(info.duration) % 60;
        if (length[1] < 10) length[1] = 0 + length[1].toString();
        console.log(length);
        return length;
      }
    });
  });
  promise.then(function(result) { // wait untill the voice message duration is known, the soundfile needs some time to load
    // run the voice message generation script with all the needed arguments,
    // e.g. python printer/voiceMsgGenerator.py -b '151023' -d '07.03.19 | 15:10' -l '4:20' -n 'Mary Jane'
    cmd.run('python printer/voiceMsgGenerator.py -b ' + barcodeData + ' -d ' + date + ' -l ' + length[0] + ':' + length[1] + 's -n ' + name);
  }, function(err) {
    console.log(err);
  });
})

// serve out any static files in the "public" HTML folder
app.use(express.static('public'))
// listen for requests on port 3000
app.listen(port, function(){
  console.log("Listening on port " + port)
})

// get the current date and time and format it for the printout
function getDateFormated(mode)   {
    var str = '';

    var currentTime = new Date();
    var hours = currentTime.getHours();
    var minutes = currentTime.getMinutes();
    var day = currentTime.getDate();
    var month = currentTime.getMonth()+1;
    var year = currentTime.getYear().toString().slice(1,3);

    if (minutes < 10) {
        minutes = '0' + minutes;
    }
    if (hours < 10) {
        hours = '0' + hours;
    }
    if (day < 10) {
        day = '0' + day;
    }
    if (month < 10) {
        month = '0' + month;
    }

    if(mode == 'short'){ // short mode is used for creating the upload directory
      str = year + month + day;
    }else{
      str += "'" + day + "." + month + "." + year + " | " + hours + ":" + minutes + "'";
    }
    console.log(str);
    return str;
}
