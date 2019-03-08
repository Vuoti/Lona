// ****************************************************************************
// This node script records voice messages and sends them with its creators
// name to the server via HTTP POST request.

// ! The microphone recording is only possible with an https connection due
// to safety restrictions of modern browsers. Therefore Ngrok has to be running
// on the same port as the server.
//
// Written by Andre Fritzinger
//
// ****************************************************************************
// To-Do:
// - There is a bug with the http-posts, sometimes they get send multiple times
// - Validation of the input form is broken (allow only characters A-Z, a-z)
// - The check if the recording button is pressed is not precise
// - Website is not responsive (Elements are on top of each other on desktop)
// - Add profile picture upload

let button, mic, soundRec, soundFile, time, input;
var isRecording = false;
var btnSize = 500;

function setup() {

  mic = new p5.AudioIn(); // Create an audio input
  mic.start(); // ! Users must manually enable their browser microphone (https connections only)

  soundRec = new p5.SoundRecorder(); // Create a sound recorder
  soundRec.setInput(mic) // Connect the microphone to the recorder

  soundFile = new p5.SoundFile(); // create an empty sound file

  // Create the Recording Button
  button = createButton("<i class=\"fa fa-microphone\" aria-hidden=\"true\">");
  button.position(window.innerWidth / 2 - 80, 2 * window.innerHeight / 3);
  document.querySelector("button").classList.add('button--record', 'button', 'js-record', 'button--disabled');

  // Create the Input field
  input = createInput().attribute('placeholder', 'Dein Name');
  input.attribute('type', 'text');
  input.attribute('pattern', '[A-Za-z]');
  input.position(window.innerWidth / 2 - input.size().width / 2, window.innerHeight / 2);
  document.getElementsByTagName("input").placeholder = "Dein Name";

}

// Enable the Recording button only if the inputfield (name) got filled in
function keyReleased() {
  if (input.value() != '') {
    document.querySelector("button").classList.remove('button--disabled');
  } else {
    document.querySelector("button").classList.add('button--disabled');
  }
}

// Start recording when the button is pressed
function mousePressed() {
  if (((dist(mouseX, mouseY, button.position().x, button.position().y + btnSize / 2)) < btnSize / 2) && (input.value() != '')) {
    document.querySelector("button").classList.add('button--active');

    // set up the soundfile to record and start recording
    getAudioContext().resume();
    soundRec.record(soundFile);
    console.log("recording....");

    time = getTime(); // Get the current time, will be used as filename
    isRecording = true;
  }
}

// If the button is released, end the recording and send the soundfile and the creators name to the server
function mouseReleased() {
  if (isRecording) {
    document.querySelector("button").classList.remove('button--active');

    soundRec.stop(); // Stop recording
    let soundBlob = soundFile.getBlob(); // Get the recorded soundFile's blob & store it in a variable

    let formdata = new FormData(); // Create a form to upload to data the server
    formdata.append('soundBlob', soundBlob, time + '.wav'); // Append the sound blob and the name of the file (will show up on the server as req.file.originalname)

    //build a HTTP POST request
    var httpRequestOptions = {
      method: 'POST',
      body: formdata,
      headers: new Headers({
        'enctype': 'multipart/form-data' // the enctype is important to work with multer on the server
      })
    };

    // Now we can send the blob to the server
    var serverUrl = '/upload'; //we've made a POST endpoint on the server at /upload

    // use p5 to make the POST request at our URL and with our options
    httpDo(
      serverUrl,
      httpRequestOptions,
      (successStatusCode) => {
        console.log("uploaded recording successfully: " + successStatusCode)
      },
      (error) => {
        console.error(error);
      }
    )

    // Prepare a second POST for the creators name
    var serverUrl = '/name';
    var postData = {
      name: input.value() // Get the input from the html form
    };

    // use p5 to make the POST request at our URL and with our options
    httpPost(
      serverUrl,
      'json',
      postData,
      function(result) {
        console.log("Sent name successfully");
      }
    );

    isRecording = false;
    console.log('recording stopped');
  }

}

// Get the time in the desired format
function getTime() {
  var str = "";

  var currentTime = new Date()
  var hours = currentTime.getHours()
  var minutes = currentTime.getMinutes()
  var seconds = currentTime.getSeconds()

  if (minutes < 10) {
    minutes = "0" + minutes
  }
  if (seconds < 10) {
    seconds = "0" + seconds
  }
  str += hours + "-" + minutes + "-" + seconds;
  return str;
}
