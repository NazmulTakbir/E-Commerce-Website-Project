window.onload=function(){
  const basicInfoForm = document.getElementById('basicInfoForm');
  const managedComplaintsForm = document.getElementById('managedComplaintsForm');
  const pendingComplaintsForm = document.getElementById('pendingComplaintsForm');
  const basicInfo = document.getElementById('basicInfo');
  const managedComplaints = document.getElementById('managedComplaints');
  const pendingComplaints = document.getElementById('pendingComplaints');

  document.getElementById("searchText").addEventListener("keydown", function(event) {
    if (event.keyCode == 13) {
      event.preventDefault();
      document.getElementById("searchIcon").click();
    }
  });

  basicInfoForm.style.display = 'block'
  managedComplaintsForm.style.display = 'none'
  pendingComplaintsForm.style.display = 'none'

  basicInfo.addEventListener('click', () => {
    basicInfoForm.style.display = 'block'
    managedComplaintsForm.style.display = 'none'
    pendingComplaintsForm.style.display = 'none'
  })

  managedComplaints.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    managedComplaintsForm.style.display = 'block'
    pendingComplaintsForm.style.display = 'none'
  })

  pendingComplaints.addEventListener('click', () => {
    basicInfoForm.style.display = 'none'
    managedComplaintsForm.style.display = 'none'
    pendingComplaintsForm.style.display = 'block'
  })

  if( document.getElementById('firstPage').innerText == 'managed' ) {
    document.getElementById('managedComplaints').click()
  }
  else if( document.getElementById('firstPage').innerText == 'pending' ) {
    document.getElementById('pendingComplaints').click()
  }
}

var allowPasswordChange = function(){
  document.getElementById('passwordChangeButton').style.display = 'none'
  document.getElementById('newPasswordDiv').style.display = 'block'
  document.getElementById('password2Div').style.display = 'block'
  document.getElementById('newPassword').required = true
  document.getElementById('password2').required = true
  document.getElementById('keepOldPassowordDiv').style.display = 'block'
}

var disallowPasswordChange = function(){
  document.getElementById('passwordChangeButton').style.display = 'block'
  document.getElementById('newPasswordDiv').style.display = 'none'
  document.getElementById('password2Div').style.display = 'none'
  document.getElementById('newPassword').required = false
  document.getElementById('password2').required = false
  document.getElementById('newPassword').value = ''
  document.getElementById('password2').value = ''
  document.getElementById('keepOldPassowordDiv').style.display = 'none'
}

var checkPassword = function() {
  if (document.getElementById('newPassword').value ==
    document.getElementById('password2').value ||
    document.getElementById('password2').value === '') {
    document.getElementById('cPassCheck').style.display = 'none';
  } else {
    document.getElementById('cPassCheck').style.display = 'block';;
  }
}

var basicInfoFormValidation = function() {
  var ok = false
  if( document.getElementById('newPassword').value ==
    document.getElementById('password2').value ) {
      ok = true
  }
  if( ok===false ) {
    $('html, body').animate({ scrollTop: 0 }, 'fast');
  }

  return ok
}
