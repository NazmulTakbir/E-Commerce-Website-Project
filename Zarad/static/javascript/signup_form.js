window.onload=function(){
  const customerForm = document.getElementById('Customer_Form');
  const sellerForm = document.getElementById('Seller_Form');
  const employeeForm = document.getElementById('Employee_Form');
  const customerButton = document.getElementById('Customer_Button');
  const sellerButton = document.getElementById('Seller_Button');
  const employeeButton = document.getElementById('Employee_Button');

  customerForm.style.display = 'block'
  sellerForm.style.display = 'none'
  employeeForm.style.display = 'none'
  document.getElementById('cPassCheck').style.display = 'none'
  document.getElementById('sPassCheck').style.display = 'none'
  document.getElementById('ePassCheck').style.display = 'none'
  document.getElementById('cImg').style.display = 'none'
  document.getElementById('sImg').style.display = 'none'
  document.getElementById('eImg').style.display = 'none'

  document.getElementsByName("customerEmail")[0].required = true;
  document.getElementsByName("customerFirstName")[0].required = true;
  document.getElementsByName("customerLastName")[0].required = true;
  document.getElementsByName("customerPassword")[0].required = true;
  document.getElementsByName("customerPassword2")[0].required = true;
  document.getElementsByName("customerArea")[0].required = true;
  document.getElementsByName("customerCity")[0].required = true;
  document.getElementsByName("customerPhNo")[0].required = true;
  document.getElementsByName("customerDOB")[0].required = true;

  document.getElementsByName("sellerName")[0].required = false;
  document.getElementsByName("sellerEmail")[0].required = false;
  document.getElementsByName("sellerArea")[0].required = false;
  document.getElementsByName("sellerCity")[0].required = false;
  document.getElementsByName("sellerPhNo")[0].required = false;
  document.getElementsByName("sellerPassword")[0].required = false;
  document.getElementsByName("sellerPassword2")[0].required = false;

  document.getElementsByName("employeeEmail")[0].required = false;
  document.getElementsByName("employeeFirstName")[0].required = false;
  document.getElementsByName("employeeLastName")[0].required = false;
  document.getElementsByName("employeeSalary")[0].required = false;
  document.getElementsByName("employeeType")[0].required = false;
  document.getElementsByName("employeePhNo")[0].required = false;
  document.getElementsByName("employeeDOB")[0].required = false;
  document.getElementsByName("employeeArea")[0].required = false;
  document.getElementsByName("employeeCity")[0].required = false;
  document.getElementsByName("employeePassword")[0].required = false;
  document.getElementsByName("employeePassword2")[0].required = false;

  customerButton.addEventListener('click', () => {
    customerForm.style.display = 'block'
    sellerForm.style.display = 'none'
    employeeForm.style.display = 'none'

    document.getElementsByName("customerEmail")[0].required = true;
    document.getElementsByName("customerFirstName")[0].required = true;
    document.getElementsByName("customerLastName")[0].required = true;
    document.getElementsByName("customerPassword")[0].required = true;
    document.getElementsByName("customerPassword2")[0].required = true;
    document.getElementsByName("customerArea")[0].required = true;
    document.getElementsByName("customerCity")[0].required = true;
    document.getElementsByName("customerPhNo")[0].required = true;
    document.getElementsByName("customerDOB")[0].required = true;

    document.getElementsByName("sellerName")[0].required = false;
    document.getElementsByName("sellerEmail")[0].required = false;
    document.getElementsByName("sellerArea")[0].required = false;
    document.getElementsByName("sellerCity")[0].required = false;
    document.getElementsByName("sellerPhNo")[0].required = false;
    document.getElementsByName("sellerPassword")[0].required = false;
    document.getElementsByName("sellerPassword2")[0].required = false;

    document.getElementsByName("employeeEmail")[0].required = false;
    document.getElementsByName("employeeFirstName")[0].required = false;
    document.getElementsByName("employeeLastName")[0].required = false;
    document.getElementsByName("employeeSalary")[0].required = false;
    document.getElementsByName("employeeType")[0].required = false;
    document.getElementsByName("employeePhNo")[0].required = false;
    document.getElementsByName("employeeDOB")[0].required = false;
    document.getElementsByName("employeeArea")[0].required = false;
    document.getElementsByName("employeeCity")[0].required = false;
    document.getElementsByName("employeePassword")[0].required = false;
    document.getElementsByName("employeePassword2")[0].required = false;
  })

  sellerButton.addEventListener('click', () => {
    customerForm.style.display = 'none'
    sellerForm.style.display = 'block'
    employeeForm.style.display = 'none'

    document.getElementsByName("customerEmail")[0].required = false;
    document.getElementsByName("customerFirstName")[0].required = false;
    document.getElementsByName("customerLastName")[0].required = false;
    document.getElementsByName("customerPassword")[0].required = false;
    document.getElementsByName("customerPassword2")[0].required = false;
    document.getElementsByName("customerArea")[0].required = false;
    document.getElementsByName("customerCity")[0].required = false;
    document.getElementsByName("customerPhNo")[0].required = false;
    document.getElementsByName("customerDOB")[0].required = false;

    document.getElementsByName("sellerName")[0].required = true;
    document.getElementsByName("sellerEmail")[0].required = true;
    document.getElementsByName("sellerArea")[0].required = true;
    document.getElementsByName("sellerCity")[0].required = true;
    document.getElementsByName("sellerPhNo")[0].required = true;
    document.getElementsByName("sellerPassword")[0].required = true;
    document.getElementsByName("sellerPassword2")[0].required = true;

    document.getElementsByName("employeeEmail")[0].required = false;
    document.getElementsByName("employeeFirstName")[0].required = false;
    document.getElementsByName("employeeLastName")[0].required = false;
    document.getElementsByName("employeeSalary")[0].required = false;
    document.getElementsByName("employeeType")[0].required = false;
    document.getElementsByName("employeePhNo")[0].required = false;
    document.getElementsByName("employeeDOB")[0].required = false;
    document.getElementsByName("employeeArea")[0].required = false;
    document.getElementsByName("employeeCity")[0].required = false;
    document.getElementsByName("employeePassword")[0].required = false;
    document.getElementsByName("employeePassword2")[0].required = false;

  })

  employeeButton.addEventListener('click', () => {
    customerForm.style.display = 'none'
    sellerForm.style.display = 'none'
    employeeForm.style.display = 'block'

    document.getElementsByName("customerEmail")[0].required = false;
    document.getElementsByName("customerFirstName")[0].required = false;
    document.getElementsByName("customerLastName")[0].required = false;
    document.getElementsByName("customerPassword")[0].required = false;
    document.getElementsByName("customerPassword2")[0].required = false;
    document.getElementsByName("customerArea")[0].required = false;
    document.getElementsByName("customerCity")[0].required = false;
    document.getElementsByName("customerPhNo")[0].required = false;
    document.getElementsByName("customerDOB")[0].required = false;

    document.getElementsByName("sellerName")[0].required = false;
    document.getElementsByName("sellerEmail")[0].required = false;
    document.getElementsByName("sellerArea")[0].required = false;
    document.getElementsByName("sellerCity")[0].required = false;
    document.getElementsByName("sellerPhNo")[0].required = false;
    document.getElementsByName("sellerPassword")[0].required = false;
    document.getElementsByName("sellerPassword2")[0].required = false;

    document.getElementsByName("employeeEmail")[0].required = true;
    document.getElementsByName("employeeFirstName")[0].required = true;
    document.getElementsByName("employeeLastName")[0].required = true;
    document.getElementsByName("employeeSalary")[0].required = true;
    document.getElementsByName("employeeType")[0].required = true;
    document.getElementsByName("employeePhNo")[0].required = true;
    document.getElementsByName("employeeDOB")[0].required = true;
    document.getElementsByName("employeeArea")[0].required = true;
    document.getElementsByName("employeeCity")[0].required = true;
    document.getElementsByName("employeePassword")[0].required = true;
    document.getElementsByName("employeePassword2")[0].required = true;
  })
}

var checkPassword = function() {
  if( document.getElementById('Customer_Button').checked ) {
    if (document.getElementById('customerPassword').value ==
      document.getElementById('customerPassword2').value ||
      document.getElementById('customerPassword2').value === '') {
      document.getElementById('cPassCheck').style.display = 'none';
    } else {
      document.getElementById('cPassCheck').style.display = 'block';;
    }
  }
  else if( document.getElementById('Seller_Button').checked ) {
    if (document.getElementById('sellerPassword').value ==
      document.getElementById('sellerPassword2').value ||
      document.getElementById('sellerPassword2').value === '') {
      document.getElementById('sPassCheck').style.display = 'none';
    } else {
      document.getElementById('sPassCheck').style.display = 'block';;
    }
  }
  else if( document.getElementById('Employee_Button').checked ) {
    if (document.getElementById('employeePassword').value ==
      document.getElementById('employeePassword2').value ||
      document.getElementById('employeePassword2').value === '') {
      document.getElementById('ePassCheck').style.display = 'none';
    } else {
      document.getElementById('ePassCheck').style.display = 'block';;
    }
  }
}

var formValidation = function() {
  var ok = false
  if( document.getElementById('Customer_Button').checked ) {
    if( document.getElementById('customerPassword').value ==
      document.getElementById('customerPassword2').value )
      ok = true
  }
  else if( document.getElementById('Seller_Button').checked ) {
    if( document.getElementById('sellerPassword').value ==
      document.getElementById('sellerPassword2').value )
      ok = true

  }
  else if( document.getElementById('Employee_Button').checked ) {
    if( document.getElementById('employeePassword').value ==
      document.getElementById('employeePassword2').value )
      ok = true

  }
  if( ok===false ) {
    $('html, body').animate({ scrollTop: 0 }, 'fast');
  }
  return ok
}

function uploadPicture(event) {
  if( document.getElementById('Customer_Button').checked ) {
    var image = document.getElementById('cImg');
  	if (event.target.files && event.target.files[0]) {
  		image.src = URL.createObjectURL(event.target.files[0]);
  		image.onload = function() {
  			image.style.width = '200px';
  			URL.revokeObjectURL(image.src) // free memory
  		}
  		document.getElementById('cImg').style.display = 'block'
  	} else {
  		image.src = "#"
  		document.getElementById('cImg').style.display = 'none'
  	}
  }
  else if( document.getElementById('Seller_Button').checked ) {
    var image = document.getElementById('sImg');
  	if (event.target.files && event.target.files[0]) {
  		image.src = URL.createObjectURL(event.target.files[0]);
  		image.onload = function() {
  			image.style.width = '200px';
  			URL.revokeObjectURL(image.src) // free memory
  		}
  		document.getElementById('sImg').style.display = 'block'
  	} else {
  		image.src = "#"
  		document.getElementById('sImg').style.display = 'none'
  	}
  }
  else if( document.getElementById('Employee_Button').checked ) {
    var image = document.getElementById('eImg');
  	if (event.target.files && event.target.files[0]) {
  		image.src = URL.createObjectURL(event.target.files[0]);
  		image.onload = function() {
  			image.style.width = '200px';
  			URL.revokeObjectURL(image.src) // free memory
  		}
  		document.getElementById('eImg').style.display = 'block'
  	} else {
  		image.src = "#"
  		document.getElementById('eImg').style.display = 'none'
  	}
  }
}
