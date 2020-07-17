var dropDownSelection = function(event) {
  document.getElementById("chosenCategory").value = event.target.innerText;
}

var addFeature = function() {
  if( document.getElementById('feature4').style.display == 'none'  ) {
    document.getElementById('feature4').style.display = 'block'
  }
  else if( document.getElementById('feature5').style.display == 'none'  ) {
    document.getElementById('feature5').style.display = 'block'
  }
  else if( document.getElementById('feature6').style.display == 'none'  ) {
    document.getElementById('feature6').style.display = 'block'
    document.getElementById('featureButton').style.display = 'none'
    document.getElementById('featureLimit').style.display = 'block'
  }
}

var formValidation = function() {
  var ok = true
  if( document.getElementById("chosenCategory").value == 'Select From Dropdown' ) {
    ok = false
    document.getElementById('errorMessageDiv').style.display = 'block';
    document.getElementById('errorMessage').innerText = 'Please Select Category';
  }
  else if( document.getElementById('pImgInput').files.length == 0 ) {
    ok = false
    document.getElementById('errorMessageDiv').style.display = 'block';
    document.getElementById('errorMessage').innerText = 'Please Select At Least 1 Picture';
  }

  if( ok===false ) {
    $('html, body').animate({ scrollTop: 0 }, 'fast');
  }
  return ok
}

function uploadPicture(event) {
  var i;
  for( i=0; i<4; i++ ) {
    image = document.getElementById('p'+(i+1).toString()+'Img')
    image.src = "#"
    image.style.display = 'none'
  }
	if (event.target.files && event.target.files[0]) {
    if( event.target.files.length > 4 ) {
      document.getElementById('errorMessageDiv').style.display = 'block';
      document.getElementById('errorMessage').innerText = 'Maximum 4 Images';
      $('html, body').animate({ scrollTop: 0 }, 'fast');
      document.getElementById('pImgInput').value = ""
    }
    else {
      var i;
      for( i=0; i<event.target.files.length && i<4; i++ ) {
        image = document.getElementById('p'+(i+1).toString()+'Img')
    		image.src = URL.createObjectURL(event.target.files[i]);
    		image.style.width = '200px';
    		image.style.display = 'block'
      }
      document.getElementById('errorMessageDiv').style.display = 'none';
      document.getElementById('errorMessage').innerText = '';
    }
	}
}
