window.onload=function(){
  const basicInfoForm = document.getElementById('basicInfoForm');
  const managedComplaintsForm = document.getElementById('managedComplaintsForm');
  const pendingComplaintsForm = document.getElementById('pendingComplaintsForm');
  const basicInfo = document.getElementById('basicInfo');
  const managedComplaints = document.getElementById('managedComplaints');
  const pendingComplaints = document.getElementById('pendingComplaints');

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
}
